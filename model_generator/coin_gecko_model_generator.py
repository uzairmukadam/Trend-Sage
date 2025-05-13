import os
import re
import pandas as pd
from pmdarima import auto_arima

class ModelGenerator:
    """
    A class to generate predictive models and forecasts from engineered datasets using ARIMA.
    """

    def __init__(self, dataset_directory='./data/engineered', forecast_directory='./data/forecast', identifier="gecko"):
        """
        Initializes the ModelGenerator.

        Args:
            dataset_directory (str): Directory containing feature-engineered datasets.
            forecast_directory (str): Directory to store forecast results.
            identifier (str): Fixed identifier used in filenames.
        """
        self.identifier = identifier
        self.dataset_directory = dataset_directory
        self.forecast_directory = forecast_directory

        # Internal attributes for tracking progress and storing data
        self.dataset_file_name = None
        self.target = 'price'
        self.data = None
        self.train = None
        self.train_exog = None
        self.model = None
        self.forecast = None
        self.future_exog_data = None

        os.makedirs(self.forecast_directory, exist_ok=True)

    def get_sorted_files(self, directory):
        """
        Retrieves all files in a directory, sorted by timestamp in the filename.

        Args:
            directory (str): The directory to list files from.

        Returns:
            list: A list of filenames sorted by timestamp.
        """
        try:
            files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            return sorted(files, key=lambda x: int(re.search(r'_(\d+)_', x).group(1)) if re.search(r'_(\d+)_', x) else 0)
        except Exception as e:
            print(f"[ERROR] Failed to retrieve files from {directory}: {e}")
            return []

    def load_data(self, timeframe):
        """
        Loads the latest dataset file that matches the timeframe and isn't already forecasted.

        Args:
            timeframe (str): The timeframe to filter files ('365days' or '90days').

        Returns:
            pd.DataFrame or None: DataFrame of the loaded CSV file, or None if no new file is found.
        """
        dataset_files = [f for f in self.get_sorted_files(self.dataset_directory) 
                         if f.startswith(self.identifier) and f.endswith(f'{timeframe}.csv')]

        forecast_files = [f for f in self.get_sorted_files(self.forecast_directory) 
                          if f.startswith(self.identifier) and f.endswith(f'{timeframe}.csv')]

        # Find the latest forecast timestamp if available
        latest_forecast_timestamp = max(
            (int(re.search(r'_(\d+)_', f).group(1)) for f in forecast_files if re.search(r'_(\d+)_', f)),
            default=None
        )

        # Load the latest dataset file that hasn't been forecasted
        for dataset_file in dataset_files:
            dataset_timestamp = int(re.search(r'_(\d+)_', dataset_file).group(1))
            if latest_forecast_timestamp is None or dataset_timestamp > latest_forecast_timestamp:
                self.dataset_file_name = dataset_file
                return pd.read_csv(os.path.join(self.dataset_directory, dataset_file))

        print(f"[INFO] No new datasets available for timeframe: '{timeframe}'.")
        return None

    def preprocess_data(self, exogenous_columns):
        """
        Preprocesses the loaded data by dropping missing values and extracting target and exogenous variables.

        Args:
            exogenous_columns (list): List of column names to use as exogenous variables.
        """
        self.data = self.data.dropna()
        self.train = self.data[self.target]
        self.train_exog = self.data[exogenous_columns]

    def fit_auto_arima(self):
        """
        Fits an ARIMA model to the training data with optional exogenous variables.
        """
        try:
            self.model = auto_arima(
                self.train,
                X=self.train_exog,
                seasonal=False,
                trace=False,
                error_action='ignore',
                suppress_warnings=True,
                stepwise=True
            )
            print("[INFO] ARIMA model successfully fitted.")
        except Exception as e:
            print(f"[ERROR] Failed to fit ARIMA model: {e}")

    def forecast_future(self, timeframe, steps=30):
        """
        Forecasts future values using the fitted ARIMA model with dynamic adjustments to exogenous variables.

        Args:
            timeframe (str): Timeframe to process ('365days' or '90days').
            steps (int): Number of future time steps to forecast.
        """
        try:
            exogenous_columns = {
                '365days': ['market_cap', 'volume', '5_day_MA', '25_day_MA', '100_day_MA'],
                '90days': ['market_cap', 'volume', '9_hr_EMA', '50_hr_EMA', '12_hr_RSI']
            }.get(timeframe, [])

            if not exogenous_columns:
                print(f"[ERROR] Invalid timeframe: {timeframe}")
                return

            recent_exog_data = self.train_exog[exogenous_columns].iloc[-steps:]

            ma_columns = [col for col in exogenous_columns if "MA" in col]
            non_ma_columns = [col for col in exogenous_columns if col not in ma_columns]

            slopes = {col: (recent_exog_data[col].iloc[-1] - recent_exog_data[col].iloc[0]) / (steps - 1) for col in non_ma_columns}

            self.future_exog_data = pd.DataFrame(columns=exogenous_columns)
            self.future_exog_data.loc[0] = recent_exog_data.iloc[-1]

            for step in range(1, steps):
                self.future_exog_data.loc[step] = self.future_exog_data.loc[0]

                for col, slope in slopes.items():
                    self.future_exog_data.loc[step, col] += slope * step

                for i in range(len(ma_columns) - 1):
                    ma1, ma2 = ma_columns[i], ma_columns[i + 1]
                    trend_direction = 1 if self.future_exog_data.loc[step - 1, ma1] > self.future_exog_data.loc[step - 1, ma2] else -1
                    self.future_exog_data.loc[step, ma1] += trend_direction * abs(self.future_exog_data.loc[step - 1, ma2] - self.future_exog_data.loc[step - 1, ma1]) * 0.1
                    self.future_exog_data.loc[step, ma2] += trend_direction * abs(self.future_exog_data.loc[step - 1, ma2] - self.future_exog_data.loc[0, ma2]) * 0.05

            self.forecast = self.model.predict(n_periods=steps, X=self.future_exog_data)

            print(f"[INFO] Forecast successfully generated for timeframe: {timeframe}.")
        except Exception as e:
            print(f"[ERROR] Failed to generate forecast: {e}")
            return None

    def save_forecast(self, steps=30):
        """
        Saves forecasted results along with all exogenous variables to a new file in the forecast directory.

        Args:
            steps (int): Number of future time steps forecasted.
        """
        if self.forecast is None or self.future_exog_data is None:
            print("[WARNING] No forecast or exogenous data available to save.")
            return
          
        forecast_file_path = os.path.join(self.forecast_directory, f"forecast_{self.dataset_file_name}")

        try:
            forecast_df = pd.DataFrame(self.forecast, columns=['price'])
            combined_df = pd.concat([forecast_df.reset_index(drop=True), self.future_exog_data.reset_index(drop=True)], axis=1)

            # Save to CSV
            combined_df.to_csv(forecast_file_path, index=False)
            print(f"[INFO] Forecast and all exogenous data successfully saved: {forecast_file_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save forecast data: {e}")

    def fit(self, timeframe, steps=30):
        """Fits a model and forecasts future values for a given timeframe."""
        print(f"[INFO] Processing timeframe: {timeframe}...")
        self.data = self.load_data(timeframe)

        if self.data is not None:
            exogenous_columns = {
                '365days': ['market_cap', 'volume', '5_day_MA', '25_day_MA', '100_day_MA'],
                '90days': ['market_cap', 'volume', '9_hr_EMA', '50_hr_EMA', '12_hr_RSI']
            }.get(timeframe, [])

            self.preprocess_data(exogenous_columns)
            self.fit_auto_arima()
            self.forecast_future(timeframe=timeframe, steps=steps)
            self.save_forecast(steps=steps)

if __name__ == '__main__':
    model_generator = ModelGenerator()
    model_generator.fit(timeframe='365days', steps=30)
    model_generator.fit(timeframe='90days', steps=30)