import requests
import json
import time
import os

class CryptoDataFetcher:
    """
    A class to interact with the CoinGecko API and fetch cryptocurrency data.
    """

    def __init__(self, data_dir='./src/data/raw'):
        """
        Initializes the CryptoDataFetcher.

        Args:
            base_url (str): The base URL for the API.
            vs_currencies (str): The target currency (e.g., 'usd').
            coin_ids (list): List of cryptocurrency IDs to fetch data for.
            data_dir (str): The directory to save fetched data.
        """
        self.base_url = "https://api.coingecko.com/api/v3"
        self.vs_currencies = "usd"
        self.coin_ids = ["bitcoin", "ethereum", "ravencoin", "tron"]
        self.data_dir = data_dir

    def make_request(self, endpoint, params=None):
        """
        Sends a GET request to the specified API endpoint.

        Args:
            endpoint (str): The API endpoint to query.
            params (dict, optional): Query parameters.

        Returns:
            dict or None: The JSON response, or None if the request fails.
        """
        url = self.base_url + endpoint
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None

    def save_to_file(self, data, filename):
        """
        Saves the provided data to a local JSON file, ensuring the directory exists.

        Args:
            data (dict): The data to save.
            filename (str): The output filename.
        """
        identifier = "gecko"
        timestamp = time.strftime("%Y%m%d%H%M%S")
        full_path = os.path.join(self.data_dir, f"{identifier}_{timestamp}_{filename}")

        try:
            os.makedirs(self.data_dir, exist_ok=True)  # Create the directory if it doesn't exist
            with open(full_path, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Data successfully saved to {full_path}")
        except IOError as e:
            print(f"Error saving data to file {full_path}: {e}")
        except OSError as e:
            print(f"Error creating directory {self.data_dir}: {e}")

    # API Calls
    def ping(self):
        data = self.make_request("/ping")
        if data:
            self.save_to_file(data, "ping.json")
        return data

    def get_coins_list(self):
        data = self.make_request("/coins/list")
        if data:
            self.save_to_file(data, "coins_list.json")
        return data

    def get_global_data(self):
        data = self.make_request("/global")
        if data:
            self.save_to_file(data, "global_data.json")
        return data

    def get_coin_data_by_id(self, coin_id):
        data = self.make_request(f"/coins/{coin_id}")
        if data:
            self.save_to_file(data, f"{coin_id}_data.json")
        return data

    def get_coin_price_by_id(self, coin_id):
        params = {
            "ids": coin_id,
            "vs_currencies": self.vs_currencies,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
            "include_last_updated_at": "true",
            "precision": 5
        }
        data = self.make_request("/simple/price", params)
        if data:
            self.save_to_file(data, f"{coin_id}_price.json")
        return data

    def get_coin_chart_year_by_id(self, coin_id):
        params = {"vs_currency": self.vs_currencies, "days": 365}
        data = self.make_request(f"/coins/{coin_id}/market_chart", params)
        if data:
            self.save_to_file(data, f"{coin_id}_market_chart_year.json")
        return data

    def get_coin_chart_90days_by_id(self, coin_id):
        params = {"vs_currency": self.vs_currencies, "days": 90}
        data = self.make_request(f"/coins/{coin_id}/market_chart", params)
        if data:
            self.save_to_file(data, f"{coin_id}_market_chart_90days.json")
        return data

    def get_coin_charts(self, coin_id):
        print(f"Fetching market charts for {coin_id}...")
        self.get_coin_chart_year_by_id(coin_id)
        self.get_coin_chart_90days_by_id(coin_id)
        print(f"Completed API calls for {coin_id}.")

    # Driver Functions
    def run_static_calls(self):
        """
        Executes static API calls that do not depend on specific coin IDs.
        """
        print("Running static API calls...")
        self.ping()
        self.get_coins_list()
        self.get_global_data()
        print("Static API calls completed.")

    def run_id_calls(self, delay=20):
        """
        Executes API calls for each coin in the predefined list of coin IDs.

        Args:
            delay (int): Time to wait (in seconds) between API calls for each coin.
        """
        print("Running ID-dependent API calls...")
        for coin_id in self.coin_ids:
            self.get_coin_charts(coin_id)
            time.sleep(delay)
        print("ID-dependent API calls completed.")


# Example Usage
if __name__ == "__main__":
    fetcher = CryptoDataFetcher()
    fetcher.run_static_calls()
