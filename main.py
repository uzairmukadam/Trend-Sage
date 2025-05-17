import time
import threading
from flask import Flask
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

# List of crypto assets
crypto_assets = ["bitcoin", "ethereum", "ravencoin"]

# Customizable delays (in seconds)
delay_between_assets = 5 * 60  # 5 minutes between assets
delay_between_cycles = 24 * 60 * 60  # 24 hours between full cycles

def run_workflow():
    while True:
        print("\n[INFO] Starting new workflow cycle...\n")

        for asset in crypto_assets:
            print(f"\n[INFO] Fetching cryptocurrency data for {asset}...\n")
            data_fetcher.get_coin_charts(asset)

            print(f"[INFO] Preprocessing raw data for {asset}...")
            preprocessor.process_raw()

            print(f"[INFO] Performing feature engineering on {asset}...")
            engineer.engineer_features()

            print(f"[INFO] Generating forecast for '365days' timeframe for {asset}...")
            model_generator.fit(timeframe='365days', steps=30)

            print(f"[INFO] Generating forecast for '90days' timeframe for {asset}...")
            model_generator.fit(timeframe='90days', steps=30)

            print(f"[INFO] Analyzing data for {asset}...")
            data_analyzer.process()

            print(f"[INFO] Completed workflow for {asset}. Waiting {delay_between_assets} seconds before next asset...")
            time.sleep(delay_between_assets)
        
        print(f"\n[INFO] Finished full cycle! Waiting {delay_between_cycles} seconds before restarting...\n")
        time.sleep(delay_between_cycles)

# Start workflow in a separate thread
workflow_thread = threading.Thread(target=run_workflow, daemon=True)
workflow_thread.start()

# Run Flask app indefinitely
app.run()
