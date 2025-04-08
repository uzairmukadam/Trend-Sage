import os
import pandas as pd
import re

class FeatureEngineer:
    """
    A class for feature engineering of processed CSV data by adding Moving Averages, 
    Exponential Moving Averages, and RSI (Relative Strength Index) calculations.
    """

    def __init__(self, preprocessed_directory='./data/processed', engineered_directory='./data/engineered', identifier="gecko"):
        """
        Initializes the FeatureEngineer instance.

        Args:
            preprocessed_directory (str): Directory containing processed CSV files.
            engineered_directory (str): Directory to store feature-engineered CSV files.
            identifier (str): Fixed identifier used in filenames.
        """
        self.identifier = identifier
        self.preprocessed_directory = preprocessed_directory
        self.engineered_directory = engineered_directory

        os.makedirs(engineered_directory, exist_ok=True)

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
            files.sort(key=lambda x: int(re.search(r'_(\d+)_', x).group(1)) if re.search(r'_(\d+)_', x) else 0)
            return files
        except Exception as e:
            print(f"[ERROR] Failed to retrieve files from {directory}: {e}")
            return []

    def get_unengineered_files(self, processed_files, engineered_files):
        """
        Identifies files present in the processed directory but missing in the engineered directory.

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
        Adds 5-day, 25-day, and 100-day Moving Averages to a daily CSV dataset.

        Args:
            file_path (str): Path to the input CSV file.
            output_directory (str): Directory to save the updated CSV file.
        """
        try:
            df = pd.read_csv(file_path)
            df.sort_values(by='timestamp', inplace=True)

            # Add Moving Averages
            df['5_day_MA'] = df['price'].rolling(window=5).mean()
            df['25_day_MA'] = df['price'].rolling(window=25).mean()
            df['100_day_MA'] = df['price'].rolling(window=100).mean()

            output_file_path = os.path.join(output_directory, os.path.basename(file_path))
            df.to_csv(output_file_path, index=False)
            print(f"[INFO] Successfully engineered daily features for {file_path} -> {output_file_path}")
        except Exception as e:
            print(f"[ERROR] Failed to engineer daily dataset for {file_path}: {e}")

    def engineer_hourly_dataset(self, file_path, output_directory):
        """
        Adds 9-hr and 50-hr Exponential Moving Averages and 12-hr RSI to an hourly CSV dataset.

        Args:
            file_path (str): Path to the input CSV file.
            output_directory (str): Directory to save the updated CSV file.
        """
        try:
            df = pd.read_csv(file_path)
            df.sort_values(by='timestamp', inplace=True)

            # Add Exponential Moving Averages
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

            # Clean up intermediate columns
            df.drop(['price_change', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rs'], axis=1, inplace=True)

            # Save to output directory
            output_file_path = os.path.join(output_directory, os.path.basename(file_path))
            df.to_csv(output_file_path, index=False)
            print(f"[INFO] Successfully engineered hourly features for {file_path} -> {output_file_path}")
        except Exception as e:
            print(f"[ERROR] Failed to engineer hourly dataset for {file_path}: {e}")

    def engineer_features(self):
        """
        Processes all CSV files in the preprocessed directory and applies feature engineering.

        Feature engineering logic is based on the last component of the filenames 
        (e.g., "year" for daily dataset, "90days" for hourly dataset).
        """
        print("[INFO] Starting feature engineering...")
        preprocessed_files = self.get_sorted_files(self.preprocessed_directory)
        engineered_files = self.get_sorted_files(self.engineered_directory)

        unengineered_files = self.get_unengineered_files(preprocessed_files, engineered_files)

        if not unengineered_files:
            print("[INFO] No new files to engineer.")
            return

        for preprocessed_file in unengineered_files:
            preprocessed_file_path = os.path.join(self.preprocessed_directory, preprocessed_file)

            last_component = preprocessed_file.split('_')[-1].lower()

            if last_component.startswith("365days"):
                self.engineer_daily_dataset(preprocessed_file_path, self.engineered_directory)

            elif last_component.startswith("90days"):
                self.engineer_hourly_dataset(preprocessed_file_path, self.engineered_directory)

        print("[INFO] Feature engineering completed for all files.")


# Example Usage
if __name__ == "__main__":
    engineer = FeatureEngineer()
    engineer.engineer_features()
