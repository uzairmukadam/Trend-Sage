from data_fetcher.coin_gecko_source import DataFetcher
from data_preprocessor.coin_gecko_preprocess import DataProcessor
from feature_engineering.coin_gecko_feature_engineering import FeatureEngineering
from model_generator.coin_gecko_model_generator import ModelGenerator

# COIN_IDS = ["bitcoin", "ethereum", "ravencoin", "tron"]

data_fetcher = DataFetcher()
preprocessor = DataProcessor()
engineer = FeatureEngineering()
model_generator = ModelGenerator()

data_fetcher.get_coin_charts("bitcoin")
preprocessor.process_raw()
engineer.engineer_features()
model_generator.fit(timeframe='year', steps=30)
model_generator.fit(timeframe='90days', steps=30)