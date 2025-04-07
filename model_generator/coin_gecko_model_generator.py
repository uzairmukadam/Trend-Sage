import os
import re
import pandas as pd
from pmdarima import auto_arima

class ModelGenerator:
    def __init__(self, dataset_directory='./data/engineered', forecast_directory='./data/forecast', identifier="gecko"):
        self.identifier = identifier
        self.dataset_directory = dataset_directory
        self.forecast_directory = forecast_directory

        self.dataset_file_name = None

        self.target = 'price'
        self.data = None
        self.train = None
        self.train_exog = None
        self.model = None
        self.forecast = None

        self.short_trend = None
        self.long_trend = None

        os.makedirs(forecast_directory, exist_ok=True)

    def get_sorted_files(self, directory):
        """
        Get all files in a directory, sorted by timestamp in filename.
        """
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        return sorted(files, key=lambda x: int(re.search(r'_(\d+)_', x).group(1)) if re.search(r'_(\d+)_', x) else 0)

    def load_data(self, timeframe):
        """
        Load the latest dataset file that matches the timeframe and is not present in the forecast directory.
        Args:
            timeframe (str): The timeframe to filter files ('year' or '90days').
        Returns:
            pd.DataFrame: Dataframe of the loaded CSV file, or None if no new file is found.
        """
        # Filter dataset files by identifier and timeframe
        dataset_files = [f for f in self.get_sorted_files(self.dataset_directory)
                        if f.startswith(self.identifier) and f.endswith(f'{timeframe}.csv')]

        # Filter forecast files by identifier and timeframe
        forecast_files = [f for f in self.get_sorted_files(self.forecast_directory)
                        if f.startswith(self.identifier) and f.endswith(f'{timeframe}.csv')]

        # Find the latest forecast timestamp, if available
        latest_forecast_timestamp = max(
            (int(re.search(r'_(\d+)_', f).group(1)) for f in forecast_files if re.search(r'_(\d+)_', f)),
            default=None
        )

        # Load the latest dataset file that is not present in the forecast directory
        for dataset_file in dataset_files:
            dataset_timestamp = int(re.search(r'_(\d+)_', dataset_file).group(1))
            if latest_forecast_timestamp is None or dataset_timestamp > latest_forecast_timestamp:
                self.dataset_file_name = dataset_file  # Save the dataset filename for reference
                return pd.read_csv(os.path.join(self.dataset_directory, dataset_file))

        # Return None if no new file is found
        return None

    def preprocess_data(self, exogenous_columns):
        """
        Preprocess the loaded data by dropping missing values and splitting into train and test sets.
        """
        self.data = self.data.dropna()

        self.train = self.data[self.target]

        self.train_exog = self.data[exogenous_columns]

    def fit_auto_arima(self):
        """
        Fit an auto_arima model to the training data with optional exogenous variables.
        """
        self.model = auto_arima(
            self.train,
            X=self.train_exog,
            seasonal=False,
            trace=False,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True
        )

    def forecast_future(self, exogenous_columns, steps=30):
        """
        Forecast future values based on the fitted model using calculated slopes and dynamic adjustments.
        Args:
            exogenous_columns (list): List of exogenous variable column names.
            steps (int): Number of future time steps to forecast.
        """
        recent_exog_data = self.train_exog[exogenous_columns].iloc[-steps:]

        slopes = [(col, (recent_exog_data[col].iloc[-1] - recent_exog_data[col].iloc[0]) / 29) for col in recent_exog_data.columns]

        # Initialize future_exog_data
        future_exog_data = pd.DataFrame(columns=exogenous_columns)

        # Set the first row as the last row of recent_exog_data
        future_exog_data.loc[0] = recent_exog_data.iloc[-1]

        # Generate future rows by applying the slope
        for step in range(1, steps):
            future_exog_data.loc[step] = [
                future_exog_data.loc[0, col] + slope * step for col, slope in slopes
            ]

        # Use the generated future_exog_data for forecasting
        self.forecast = self.model.predict(n_periods=steps, X=future_exog_data)

    def save_forecast(self, steps=30):
        """
        Save forecasted results to a new file in the forecast directory.
        """
        if self.forecast is not None:
            forecast_file_path = os.path.join(self.forecast_directory, self.dataset_file_name)
            pd.DataFrame({'step': range(1, steps + 1), 'forecast': self.forecast}).to_csv(forecast_file_path, index=False)
            print(f"Forecast saved to {forecast_file_path}")
        else:
            print("No forecast to save.")

    def fit(self, timeframe, steps=30):
        """
        General fit method for both daily and hourly fitting.
        """
        self.data = self.load_data(timeframe)

        if timeframe == 'year':
            exogenous_columns=['market_cap', 'volume', '5_day_MA', '25_day_MA', '100_day_MA']
        elif timeframe == '90days':
            exogenous_columns=['market_cap', 'volume', '9_hr_EMA', '50_hr_EMA', '12_hr_RSI']

        if self.data is not None:
            self.preprocess_data(exogenous_columns)
            self.fit_auto_arima()
            self.forecast_future(exogenous_columns=exogenous_columns, steps=steps)
            self.save_forecast(steps)
        else:
            print(f"No new data available for timeframe '{timeframe}'.")

if __name__ == '__main__':
    model_generator = ModelGenerator()
    model_generator.fit(timeframe='year', steps=30)
    model_generator.fit(timeframe='90days', steps=30)
