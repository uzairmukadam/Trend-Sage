import requests
import json
import time
import os

class DataFetcher:
    """
    A class to interact with the CoinGecko API and fetch cryptocurrency data.
    """

    def __init__(self, data_dir='./data/raw'):
        """
        Initializes the DataFetcher instance.

        Args:
            data_dir (str): Directory where fetched data will be saved.
        """
        self.base_url = "https://api.coingecko.com/api/v3"
        self.vs_currencies = "usd"
        self.coin_ids = ["bitcoin", "ethereum", "ravencoin", "tron"]
        self.data_dir = data_dir

        os.makedirs(data_dir, exist_ok=True)

    def make_request(self, endpoint, params=None):
        """
        Sends a GET request to the specified API endpoint.

        Args:
            endpoint (str): The API endpoint to query.
            params (dict, optional): Query parameters.

        Returns:
            dict: JSON response from the API, or None if an error occurs.
        """
        url = self.base_url + endpoint
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch data from {url}: {e}")
            return None

    def save_to_file(self, data, filename):
        """
        Saves the data to a local JSON file.

        Args:
            data (dict): Data to save.
            filename (str): Name of the file to save the data in.
        """
        identifier = "gecko"
        timestamp = time.strftime("%Y%m%d%H%M%S")
        full_path = os.path.join(self.data_dir, f"{identifier}_{timestamp}_{filename}")

        try:
            with open(full_path, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"[INFO] Data successfully saved to: {full_path}")
        except (IOError, OSError) as e:
            print(f"[ERROR] Unable to save data to {full_path}: {e}")

    def ping(self):
        """
        Tests the API connection.

        Returns:
            dict: Response from the API.
        """
        print("[INFO] Pinging the API...")
        data = self.make_request("/ping")
        if data:
            self.save_to_file(data, "ping.json")
        return data

    def get_coins_list(self):
        """
        Fetches the list of available cryptocurrencies.

        Returns:
            dict: JSON response containing the list of coins.
        """
        print("[INFO] Fetching the list of coins...")
        data = self.make_request("/coins/list")
        if data:
            self.save_to_file(data, "coins_list.json")
        return data

    def get_global_data(self):
        """
        Fetches global market data for cryptocurrencies.

        Returns:
            dict: JSON response containing global market data.
        """
        print("[INFO] Fetching global cryptocurrency data...")
        data = self.make_request("/global")
        if data:
            self.save_to_file(data, "global_data.json")
        return data

    def get_coin_data_by_id(self, coin_id):
        """
        Fetches detailed data for a specific cryptocurrency.

        Args:
            coin_id (str): ID of the cryptocurrency.

        Returns:
            dict: JSON response for the specified cryptocurrency.
        """
        print(f"[INFO] Fetching data for coin: {coin_id}")
        data = self.make_request(f"/coins/{coin_id}")
        if data:
            self.save_to_file(data, f"{coin_id}_data.json")
        return data

    def get_coin_price_by_id(self, coin_id):
        """
        Fetches the price data for a specific cryptocurrency.

        Args:
            coin_id (str): ID of the cryptocurrency.

        Returns:
            dict: JSON response containing price details.
        """
        print(f"[INFO] Fetching price data for coin: {coin_id}")
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

    def get_coin_chart(self, coin_id, days):
        """
        Fetches market chart data for a specific cryptocurrency.

        Args:
            coin_id (str): ID of the cryptocurrency.
            days (int): Number of days for historical data.

        Returns:
            dict: JSON response containing chart data.
        """
        print(f"[INFO] Fetching {days}-day chart data for coin: {coin_id}")
        params = {"vs_currency": self.vs_currencies, "days": days}
        data = self.make_request(f"/coins/{coin_id}/market_chart", params)
        if data:
            self.save_to_file(data, f"{coin_id}_market_chart_{days}days.json")
        return data

    def get_coin_charts(self, coin_id):
        """
        Fetches 1-year and 90-day market chart data for a specific cryptocurrency.

        Args:
            coin_id (str): ID of the cryptocurrency.
        """
        print(f"[INFO] Fetching market charts for coin: {coin_id}")
        self.get_coin_chart(coin_id, 365)
        self.get_coin_chart(coin_id, 90)
        print(f"[INFO] Completed fetching market charts for coin: {coin_id}")

    def run_static_calls(self):
        """
        Executes API calls that do not depend on specific coin IDs.
        """
        print("[INFO] Running static API calls...")
        self.ping()
        self.get_coins_list()
        self.get_global_data()
        print("[INFO] Static API calls completed.")

    def run_id_calls(self, delay=20):
        """
        Executes API calls for predefined coin IDs, with a delay between each.

        Args:
            delay (int): Time to wait (in seconds) between API calls for each coin.
        """
        print("[INFO] Running ID-dependent API calls...")
        for coin_id in self.coin_ids:
            self.get_coin_charts(coin_id)
            time.sleep(delay)
        print("[INFO] ID-dependent API calls completed.")


# Example Usage
if __name__ == "__main__":
    fetcher = DataFetcher()
    fetcher.get_coin_charts('ethereum')
