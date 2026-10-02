import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# تحديد المسار الرئيسي للمشروع لقراءة ملفات النموذج
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# تحميل النموذج وملفات المعالجة
with open(os.path.join(PARENT_DIR, 'model.pkl'), 'rb') as f:
    model = pickle.load(f)
with open(os.path.join(PARENT_DIR, 'columns.pkl'), 'rb') as f:
    train_columns = pickle.load(f)
with open(os.path.join(PARENT_DIR, 'scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)

# تعريف الأعمدة
SKEWED = ['capital-gain', 'capital-loss']
NUMERICAL = ['age', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week']

def preprocess(input_dict):
    # 1. تحويل البيانات المدخلة إلى DataFrame
    df = pd.DataFrame([input_dict])
    
    # 2. التأكد من أن الأرقام مدخلة كأرقام وليست نصوص
    for col in NUMERICAL:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3. تعديل القيم الملتوية (Skewed Data)
    df[SKEWED] = df[SKEWED].apply(lambda x: np.log1p(np.maximum(0, x)))

    # 4. تحجيم الأرقام باستخدام Scaler
    df[NUMERICAL] = scaler.transform(df[NUMERICAL])

    # 5. تحويل النصوص إلى One-Hot Encoding
    df_encoded = pd.get_dummies(df)

    # 6. ترتيب الأعمدة لتمائل الأعمدة التي تدرب عليها النموذج بالضبط
    df_encoded = df_encoded.reindex(columns=train_columns, fill_value=0)
    
    return df_encoded

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # استقبال البيانات المكتوبة بصيغة JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        # معالجة البيانات
        processed = preprocess(data)
        
        # التنبؤ باستخدام النموذج
        prediction = model.predict(processed)[0]
        
        # حساب الاحتمالية
        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(processed)[0][1]
        else:
            probability = 1.0 if prediction == 1 else 0.0

        # إرجاع النتيجة
        return jsonify({
            "prediction": ">50K" if prediction == 1 else "<=50K",
            "probability": round(float(probability), 4)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)