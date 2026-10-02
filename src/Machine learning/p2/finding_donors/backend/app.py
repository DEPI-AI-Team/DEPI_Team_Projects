import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(PARENT_DIR, 'model.pkl'), 'rb') as f:
    model = pickle.load(f)
with open(os.path.join(PARENT_DIR, 'columns.pkl'), 'rb') as f:
    train_columns = pickle.load(f)
with open(os.path.join(PARENT_DIR, 'scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)

SKEWED = ['capital-gain', 'capital-loss']
NUMERICAL = ['age', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week']

def preprocess(input_dict):
    df = pd.DataFrame([input_dict])
    df[SKEWED] = df[SKEWED].apply(lambda x: np.log(x + 1))
    df[NUMERICAL] = scaler.transform(df[NUMERICAL])
    df_encoded = pd.get_dummies(df)
    df_encoded = df_encoded.reindex(columns=train_columns, fill_value=0)
    return df_encoded

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        processed = preprocess(data)
        prediction = model.predict(processed)[0]
        probability = model.predict_proba(processed)[0][1]

        return jsonify({
            "prediction": ">50K" if prediction == 1 else "<=50K",
            "probability": round(float(probability), 4)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)