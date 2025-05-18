# Crypto Data Analysis and Forecasting Pipeline

This project is a comprehensive cryptocurrency data analysis and forecasting pipeline that fetches, preprocesses, engineers features, and builds predictive models for cryptocurrencies. It consists of multiple modules to streamline the end-to-end process from data collection to actionable insights.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Directory Structure](#-directory-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Modules](#-modules)
  - [1. DataFetcher](#1-datafetcher)
  - [2. DataProcessor](#2-dataprocessor)
  - [3. FeatureEngineer](#3-featureengineer)
  - [4. ModelGenerator](#4-modelgenerator)
  - [5. DataAnalysis](#5-dataanalysis)
  - [6. Visualizer](#6-visualizer)
- [Pending Work](#-pending-work)
- [Future Enhancements](#-future-enhancements)
- [License](#-license)

---

## 🌟 Overview

This project leverages the [CoinGecko API](https://www.coingecko.com/en/api) to fetch cryptocurrency data and processes it through a series of steps: raw data fetching, preprocessing, feature engineering, and predictive modeling. The ultimate goal is to forecast cryptocurrency prices and trends using a robust and modular workflow.

---

## ✨ Features
- Fetches cryptocurrency data from the CoinGecko API.
- Preprocesses raw JSON files and converts them into structured CSV files.
- Engineers features like moving averages, exponential moving averages, and RSI.
- Generates price forecasts using ARIMA-based models.
- Modularized pipeline for extensibility and reuse.
- Automated analysis.
- Flask application to visualize the analysis.

---

## 🗂 Directory Structure

```plaintext
crypto-forecast-pipeline/
│
├── data/                  # All data files
│   ├── raw/               # Raw JSON data
│   ├── processed/         # Processed CSV data
│   ├── engineered/        # Feature-engineered data
│   └── forecast/          # Forecast results
│   └── analysis/          # Analysis results
│
├── data_fetcher/          # DataFetcher module
│   └── coin_gecko_source.py
│
├── preprocessing/         # DataProcessor module
│   └── coin_gecko_preprocess.py
│
├── feature_engineering/   # FeatureEngineer module
│   └── coin_gecko_feature_engineering.py
│
├── model_generator/       # ModelGenerator module
│   └── coin_gecko_model_generator.py
|
├── data_analyzer/         # DataAnalysis module
│   └── coin_gecko_data_analyzer.py
|
├── visualizer/            # Data visualizer app
│   └── data_visualizer.py
│
├── main.py                # Main script to run the workflow
├── README.md              # Project README
└── requirements.txt       # Python dependencies
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Virtual environment (optional but recommended)

### Steps

1. Clone this repository.
2. Set up a virtual environment.
3. Install the dependencies.

---

## 🛠 Usage

1. Run the main pipeline.
2. Customize the pipeline by modifying the main.py file:
    - Add or remove cryptocurrencies in the CryptoDataFetcher class.
    - Modify feature engineering logic in FeatureEngineer.
    - Adjust forecasting steps or timeframes in ModelGenerator.

---

## 🧩 Modules

### 1. DataFetcher

- Location: data_fetcher/coin_gecko_source.py
- Purpose: Fetches raw cryptocurrency data from the CoinGecko API.
- Key Methods:
    - get_coin_charts(coin_id): Fetches market chart data for a specific cryptocurrency.

### 2. DataProcessor

- Location: preprocessing/coin_gecko_preprocess.py
- Purpose: Converts raw JSON files to CSV format and performs basic data cleaning.
- Key Methods:
    - process_raw(): Processes all unprocessed raw files in the data directory.

### 3. FeatureEngineer

- Location: feature_engineering/coin_gecko_feature_engineering.py
- Purpose: Adds features like moving averages and RSI to processed data.
- Key Methods:
    - engineer_features(): Applies feature engineering to datasets based on their timeframes.

### 4. ModelGenerator

- Location: model_generator/coin_gecko_model_generator.py
- Purpose: Builds predictive models and generates forecasts using ARIMA.
- Key Methods:
    - fit(timeframe, steps): Fits a model and forecasts future prices for a given timeframe.

### 5. DataAnalysis

- Location: data_analyzer/coin_gecko_data_analyzer.py
- Purpose: Using the engineered and forecast data, generates the analysis.
- Key Methods:
    - process(): Reads the engineered and forecast data and generates basic analysis.

### 6. Visualizer

- Location: visualizer/data_visualizer.py
- Purpose: Runs a Flask application to visualize the analysis and predication.
- Key Methods:
    - run(): Starts the flask application.

---

## 🚧 Pending Work

- Enhance the accuracy and reliability of forecasting models by fine-tuning key parameters.
- Streamline the existing forecasting pipeline for better performance and efficiency.

---

## 🔮 Future Enhancements

- Experiment to include cutting-edge models such as LSTM and Prophet for improved predictions.
- Introduce additional technical indicators to enrich the dataset and boost model performance.
- Simplify the process of migrating the solution to cloud environments for scalability and accessibility.

---

## 📜 License

This project is licensed under the GNU General Public License. For detailed terms and conditions, please refer to the LICENSE file included in this repository.
