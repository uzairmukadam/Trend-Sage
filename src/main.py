from data_fetcher.coin_gecko_source import CryptoDataFetcher
from preprocessing.coin_gecko_preprocess import DataProcessor

# COIN_IDS = ["bitcoin", "ethereum", "ravencoin", "tron"]

data_fetcher = CryptoDataFetcher()
preprocessor = DataProcessor()

data_fetcher.get_coin_charts("bitcoin")
preprocessor.process_raw()