import os
import pandas as pd
import re

class FeatureEngineering:
    def __init__(self, preprocessed_directory='./src/data/processed', engineered_directory='./src/data/engineered', identifier="gecko"):
        self.identifier = identifier
        self.preprocessed_directory = preprocessed_directory
        self.engineered_directory = engineered_directory

        os.makedirs(engineered_directory, exist_ok=True)

    def get_sorted_files(self, directory):
        """
        Get all files in a directory, sorted by timestamp in filename.

        Args:
            directory (str): The directory to list files from.

        Returns:
            list: A list of filenames sorted by timestamp.
        """
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        files.sort(key=lambda x: int(re.search(r'_(\d+)_', x).group(1)) if re.search(r'_(\d+)_', x) else 0)
        return files

    def get_unengineered_files(self, processed_files, engineered_files):
        """
        Get files that are present in processed but missing in engineered.

        Args:
            processed_files (list): List of files in the processed directory.
            engineered_files (list): List of files in the engineered directory.

        Returns:
            list: A list of filenames missing from the engineered directory.
        """
        engineered_set = {f for f in engineered_files if self.identifier in f}
        unengineered_files = [f for f in processed_files if f not in engineered_set]
        return unengineered_files

    def engineer_daily_dataset(self, file_path, output_directory):
        """
        Add 5-day, 25-day, and 100-day Moving Averages to a CSV file and save it to a new directory.

        Args:
            file_path (str): Path to the CSV file to process.
            output_directory (str): Directory to save the updated file.

        Returns:
            pd.DataFrame: DataFrame with added Moving Average columns.
        """
        df = pd.read_csv(file_path)

        df = df.sort_values(by='timestamp')

        df['5_day_MA'] = df['price'].rolling(window=5).mean()
        df['25_day_MA'] = df['price'].rolling(window=25).mean()
        df['100_day_MA'] = df['price'].rolling(window=100).mean()

        output_file_path = os.path.join(output_directory, os.path.basename(file_path))
        df.to_csv(output_file_path, index=False)

    def engineer_hourly_dataset(self, file_path, output_directory):
        """
        Add 9-hr and 50-hr Exponential Moving Averages and 12-hr RSI to a CSV file 
        and save it to a new directory.

        Args:
            file_path (str): Path to the CSV file to process.
            output_directory (str): Directory to save the updated file.

        Returns:
            pd.DataFrame: DataFrame with added EMA and RSI columns.
        """
        df = pd.read_csv(file_path)

        df = df.sort_values(by='timestamp')

        df['9_hr_EMA'] = df['price'].ewm(span=9, adjust=False).mean()
        df['50_hr_EMA'] = df['price'].ewm(span=50, adjust=False).mean()

        # Calculate RSI
        df['price_change'] = df['price'].diff()
        df['gain'] = df['price_change'].apply(lambda x: x if x > 0 else 0)
        df['loss'] = df['price_change'].apply(lambda x: -x if x < 0 else 0)
        df['avg_gain'] = df['gain'].rolling(window=12).mean()
        df['avg_loss'] = df['loss'].rolling(window=12).mean()
        df['rs'] = df['avg_gain'] / df['avg_loss']
        df['12_hr_RSI'] = 100 - (100 / (1 + df['rs']))

        # Drop intermediate columns to keep the DataFrame clean
        df.drop(['price_change', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rs'], axis=1, inplace=True)

        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Save the updated file to the new directory with the original filename
        output_file_path = os.path.join(output_directory, os.path.basename(file_path))
        df.to_csv(output_file_path, index=False)


    def engineer_features(self):
        """
        Process all CSV files in the preprocessed directory and apply feature engineering
        (e.g., Moving Average, Exponential Moving Average, or RSI) based on the last term in filenames.
        """
        preprocessed_files = self.get_sorted_files(self.preprocessed_directory)
        engineered_files = self.get_sorted_files(self.engineered_directory)

        unengineered_files = self.get_unengineered_files(preprocessed_files, engineered_files)

        for preprocessed_file in unengineered_files:
            preprocessed_file_path = os.path.join(self.preprocessed_directory, preprocessed_file)

            last_component = preprocessed_file.split('_')[-1].lower()

            if last_component.startswith("year"):
                output_directory = self.engineered_directory
                self.engineer_daily_dataset(preprocessed_file_path, output_directory)

            elif last_component.startswith("90days"):
                output_directory = self.engineered_directory
                self.engineer_hourly_dataset(preprocessed_file_path, output_directory)



# Example Usage
if __name__ == "__main__":
    engineer = FeatureEngineering()
    engineer.engineer_features()
