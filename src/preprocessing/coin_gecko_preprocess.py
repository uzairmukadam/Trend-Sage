import os
import json
import csv
import re

class DataProcessor:
    """
    A class to handle the processing of raw JSON data files and converting them to CSV format.
    """

    def __init__(self, raw_directory='./src/data/raw', processed_directory='./src/data/processed', identifier="gecko"):
        """
        Initializes the DataProcessor.

        Args:
            raw_directory (str): Directory containing raw JSON files.
            processed_directory (str): Directory to store processed CSV files.
            identifier (str): Fixed identifier used in filenames.
        """
        self.raw_directory = raw_directory
        self.processed_directory = processed_directory
        self.identifier = identifier

        os.makedirs(processed_directory, exist_ok=True)

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

    def get_unprocessed_files(self, raw_files, processed_files):
        """
        Get files that are present in raw but missing in processed.

        Args:
            raw_files (list): List of files in the raw directory.
            processed_files (list): List of files in the processed directory.

        Returns:
            list: A list of filenames missing from the processed directory.
        """
        processed_set = {f for f in processed_files if self.identifier in f}
        unprocessed_files = [f for f in raw_files if f.replace('.json', '.csv') not in processed_set]
        return unprocessed_files

    def convert_json_to_csv(self, raw_file_path, csv_file_path):
        """
        Convert a JSON file with prices, market caps, and total volumes 
        to a CSV file with columns timestamp, price, market_cap, and volume.

        Args:
            raw_file_path (str): Path to the JSON file.
            csv_file_path (str): Path to the output CSV file.
        """
        try:
            with open(raw_file_path, 'r') as json_file:
                data = json.load(json_file)

            prices = data.get("prices", [])
            market_caps = data.get("market_caps", [])
            total_volumes = data.get("total_volumes", [])

            if not (len(prices) == len(market_caps) == len(total_volumes)):
                raise ValueError("Mismatch in data lengths for prices, market_caps, and total_volumes.")

            rows = []
            for i in range(len(prices)):
                rows.append({
                    "timestamp": prices[i][0],
                    "price": prices[i][1],
                    "market_cap": market_caps[i][1],
                    "volume": total_volumes[i][1]
                })

            with open(csv_file_path, 'w', newline='') as csv_file:
                fieldnames = ["timestamp", "price", "market_cap", "volume"]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            print(f"Converted {raw_file_path} to {csv_file_path}")
        except Exception as e:
            print(f"Error converting {raw_file_path} to CSV: {e}")

    def process_raw(self):
        """
        Process all raw JSON files in the raw directory and convert them to CSV format.
        """
        raw_files = self.get_sorted_files(self.raw_directory)
        processed_files = self.get_sorted_files(self.processed_directory)

        unprocessed_files = self.get_unprocessed_files(raw_files, processed_files)

        for raw_file in unprocessed_files:
            raw_file_path = os.path.join(self.raw_directory, raw_file)
            csv_file_name = raw_file.replace('.json', '.csv')
            csv_file_path = os.path.join(self.processed_directory, csv_file_name)

            self.convert_json_to_csv(raw_file_path, csv_file_path)


# Example Usage
if __name__ == "__main__":
    # Initialize the DataProcessor object
    processor = DataProcessor()

    # Ensure the processed directory exists
    os.makedirs(processor.processed_directory, exist_ok=True)

    # Process raw JSON files to CSV
    processor.process_raw()
