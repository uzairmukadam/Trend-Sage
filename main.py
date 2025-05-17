from data_fetcher.coin_gecko_data_fetcher import DataFetcher
from data_preprocessor.coin_gecko_data_preprocessor import DataPreprocessor
from feature_engineer.coin_gecko_feature_engineering import FeatureEngineer
from model_generator.coin_gecko_model_generator import ModelGenerator
from data_analyzer.coin_gecko_data_analyzer import DataAnalysis
from visualizer.data_visualizer import *

# Initialize module instances
data_fetcher = DataFetcher()
preprocessor = DataPreprocessor()
engineer = FeatureEngineer()
model_generator = ModelGenerator()
data_analyzer = DataAnalysis()

# Workflow execution
print("[INFO] Fetching cryptocurrency data...")
data_fetcher.get_coin_charts("bitcoin")

print("[INFO] Preprocessing raw data...")
preprocessor.process_raw()

print("[INFO] Performing feature engineering...")
engineer.engineer_features()

print("[INFO] Generating forecast for '365days' timeframe...")
model_generator.fit(timeframe='365days', steps=30)

print("[INFO] Generating forecast for '90days' timeframe...")
model_generator.fit(timeframe='90days', steps=30)

print("[INFO] Analyzing data...")
data_analyzer.process()

print("[INFO] Workflow completed successfully.")

app.run()
