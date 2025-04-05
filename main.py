from data_fetcher.coin_gecko_source import CryptoDataFetcher
from preprocessing.coin_gecko_preprocess import DataProcessor
from feature_engineering.coin_gecko_feature_engineering import FeatureEngineering

# COIN_IDS = ["bitcoin", "ethereum", "ravencoin", "tron"]

data_fetcher = CryptoDataFetcher()
preprocessor = DataProcessor()
engineer = FeatureEngineering()

data_fetcher.get_coin_charts("ravencoin")
preprocessor.process_raw()
engineer.engineer_features()