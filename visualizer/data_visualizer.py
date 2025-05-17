from flask import Flask, jsonify, render_template
import os
import json
import pandas as pd

app = Flask(__name__, static_folder="frontend", template_folder="frontend")
DATA_DIR = "data/analysis"

def get_available_data():
    files = os.listdir(DATA_DIR)
    csv_files = {f[:-4] for f in files if f.endswith(".csv")}
    json_files = {f[:-5] for f in files if f.endswith(".json")}
    return csv_files.intersection(json_files)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_names')
def get_names():
    return jsonify({"datasets": list(get_available_data())})

@app.route('/get_data/<name>')
def get_data(name):
    if name not in get_available_data():
        return jsonify({"error": "File pair not found"}), 404

    try:
        csv_path = os.path.join(DATA_DIR, f"{name}.csv")
        df = pd.read_csv(csv_path)

        df = df.replace({float('nan'): None})

        if "timestamp" in df.columns:
            df["timestamp"] = df["timestamp"].astype(str)

        json_path = os.path.join(DATA_DIR, f"{name}.json")
        with open(json_path, 'r') as f:
            analysis_data = json.load(f)

        return jsonify({"chart": df.to_dict(orient="records"), "analysis": analysis_data})

    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
