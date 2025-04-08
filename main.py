from data_fetcher.coin_gecko_data_fetcher import DataFetcher
from data_preprocessor.coin_gecko_data_preprocessor import DataPreprocessor
from feature_engineer.coin_gecko_feature_engineering import FeatureEngineer
from model_generator.coin_gecko_model_generator import ModelGenerator

# COIN_IDS = ["bitcoin", "ethereum", "ravencoin", "tron"]

data_fetcher = DataFetcher()
preprocessor = DataPreprocessor()
engineer = FeatureEngineer()
model_generator = ModelGenerator()

data_fetcher.get_coin_charts("bitcoin")
preprocessor.process_raw()
engineer.engineer_features()
model_generator.fit(timeframe='year', steps=30)
model_generator.fit(timeframe='90days', steps=30)