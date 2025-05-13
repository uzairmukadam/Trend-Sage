import os
import json
import pandas as pd

class DataAnalysis:
    """
    A class to analyze merged cryptocurrency data from engineered and forecasted datasets.
    """

    def __init__(self, engineered_directory='./data/engineered', forecast_directory='./data/forecast', analysis_directory='./data/analysis', identifier="gecko"):
        """
        Initializes the DataAnalysis class.

        Args:
            engineered_directory (str): Directory containing engineered datasets.
            forecast_directory (str): Directory containing forecasted datasets.
            analysis_directory (str): Directory to store analysis results.
            identifier (str): Fixed identifier used in filenames.
        """
        self.identifier = identifier
        self.engineered_directory = engineered_directory
        self.forecast_directory = forecast_directory
        self.analysis_directory = analysis_directory

        # Ensure analysis directory exists
        os.makedirs(analysis_directory, exist_ok=True)

    def get_files(self, directory):
        """Retrieves files from a directory and returns a set of filenames (without extensions)."""
        try:
            return {os.path.splitext(f)[0] for f in os.listdir(directory) if f.startswith(self.identifier) and f.endswith('.csv')}
        except Exception as e:
            print(f"[ERROR] Failed to retrieve files from {directory}: {e}")
            return set()

    def load_matching_data(self):
        """
        Loads matching engineered and forecasted datasets based on their filenames.

        Returns:
            dict: A dictionary containing matched datasets, keyed by filename.
        """
        engineered_files = self.get_files(self.engineered_directory)
        forecast_files = self.get_files(self.forecast_directory)

        matched_files = engineered_files.intersection(forecast_files)

        if not matched_files:
            print("[INFO] No matching datasets found.")
            return {}

        datasets = {}
        for filename in matched_files:
            try:
                engineered_df = pd.read_csv(os.path.join(self.engineered_directory, f"{filename}.csv"))
                forecast_df = pd.read_csv(os.path.join(self.forecast_directory, f"{filename}.csv"))
                datasets[filename] = (engineered_df, forecast_df)
            except Exception as e:
                print(f"[ERROR] Failed to load data for {filename}: {e}")

        return datasets

    def merge_data(self, engineered_df, forecast_df):
        """
        Merges engineered data with forecasted data, generating timestamps based on known intervals while preserving millisecond format.

        Args:
            engineered_df (pd.DataFrame): Engineered dataset containing timestamps.
            forecast_df (pd.DataFrame): Forecasted dataset without timestamps.

        Returns:
            pd.DataFrame: Merged dataset with aligned timestamps.
        """
        if 'timestamp' not in engineered_df.columns:
            print("[ERROR] Engineered dataset is missing 'timestamp' column.")
            return None

        # Ensure timestamps remain as integers
        engineered_df['timestamp'] = engineered_df['timestamp'].astype(int)

        # Calculate average interval between timestamps
        time_diff = engineered_df['timestamp'].diff().dropna().mean()

        if pd.isnull(time_diff):
            print("[ERROR] Unable to determine timestamp interval.")
            return None

        # Generate new timestamps for forecast data while maintaining millisecond format
        last_timestamp = engineered_df['timestamp'].iloc[-1]
        forecast_timestamps = [int(last_timestamp + (time_diff * i)) for i in range(1, len(forecast_df) + 1)]

        # Assign generated timestamps to forecast data
        forecast_df.insert(0, 'timestamp', forecast_timestamps)

        # Merge datasets by concatenation
        merged_df = pd.concat([engineered_df, forecast_df], axis=0).reset_index(drop=True)

        return merged_df

    def analyze_data(self, merged_df):
        """
        Performs trend analysis, support/resistance level identification, and generates a buy/sell/hold score.

        Args:
            merged_df (pd.DataFrame): The merged dataset to analyze.

        Returns:
            dict: Analysis results containing trend, support/resistance levels, and recommendations.
        """
        analysis_results = {}

        ma_short = merged_df.get('5_day_MA')
        ma_long = merged_df.get('25_day_MA')

        if ma_short is not None and ma_long is not None:
            analysis_results['trend'] = "Uptrend" if ma_short.iloc[-1] > ma_long.iloc[-1] else "Downtrend"
        else:
            analysis_results['trend'] = "Unknown"

        analysis_results['support'] = merged_df['price'].min() if 'price' in merged_df.columns else None
        analysis_results['resistance'] = merged_df['price'].max() if 'price' in merged_df.columns else None

        if analysis_results['trend'] == "Uptrend":
            analysis_results['recommendation'] = "Buy"
        elif analysis_results['trend'] == "Downtrend":
            analysis_results['recommendation'] = "Sell"
        else:
            analysis_results['recommendation'] = "Hold"

        return analysis_results

    def save_analysis(self, filename, merged_df, analysis_results):
        """
        Saves merged DataFrame as a CSV file and analysis results as a JSON file.

        Args:
            filename (str): Base filename for the analysis file.
            merged_df (pd.DataFrame): Merged dataset to be saved.
            analysis_results (dict): Analysis results.
        """
        merged_file_path = os.path.join(self.analysis_directory, f"{filename}.csv")
        analysis_file_path = os.path.join(self.analysis_directory, f"{filename}.json")

        try:
            # Save merged data as CSV
            merged_df.to_csv(merged_file_path, index=False)
            print(f"[INFO] Merged data saved to: {merged_file_path}")

            # Save analysis results as JSON
            with open(analysis_file_path, 'w') as f:
                json.dump(analysis_results, f, indent=4)
            print(f"[INFO] Analysis results saved to: {analysis_file_path}")

        except Exception as e:
            print(f"[ERROR] Failed to save analysis data: {e}")

    def process(self):
        """
        Runs the entire analysis workflow: loading, merging, analyzing, and saving results.
        """
        datasets = self.load_matching_data()

        if not datasets:
            print("[INFO] No valid datasets available for analysis.")
            return

        for filename, (engineered_df, forecast_df) in datasets.items():
            merged_df = self.merge_data(engineered_df, forecast_df)

            if merged_df is not None:
                analysis_results = self.analyze_data(merged_df)
                self.save_analysis(filename, merged_df, analysis_results)
            else:
                print(f"[INFO] Skipping analysis for {filename} due to merging issues.")

# Example usage
if __name__ == '__main__':
    analysis = DataAnalysis()
    analysis.process()
