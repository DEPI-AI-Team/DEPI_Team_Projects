import os
import pickle
import numpy as np
from flask import Flask, render_template, request

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

template_folder = os.path.join(parent_dir, 'templates')
static_folder = os.path.join(parent_dir, 'static')

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

model_path = os.path.join(parent_dir, 'boston_housing_model.pkl')
with open(model_path, 'rb') as file:
    model = pickle.load(file)

@app.route('/')
def home():
    return render_template('index.html', prediction_text=None)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        rm = float(request.form['RM'])
        lstat = float(request.form['LSTAT'])
        ptratio = float(request.form['PTRATIO'])

        features = np.array([[rm, lstat, ptratio]])
        prediction = model.predict(features)[0]

        formatted_price = f"${prediction:,.2f}"

        return render_template('index.html', prediction_text=formatted_price)
    except Exception as e:
        return render_template('index.html', prediction_text=f"Error: {e}")

if __name__ == '__main__':
    app.run(debug=True)