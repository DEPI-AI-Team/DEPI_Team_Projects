import os
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Predict")
st.title("🔮 Predict Income")

# إصلاح مسار قراءة ملف CSV
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

if os.path.exists(os.path.join(CURRENT_DIR, 'census.csv')):
    CSV_PATH = os.path.join(CURRENT_DIR, 'census.csv')
elif os.path.exists(os.path.join(PARENT_DIR, 'census.csv')):
    CSV_PATH = os.path.join(PARENT_DIR, 'census.csv')
else:
    CSV_PATH = os.path.join(os.path.dirname(PARENT_DIR), 'census.csv')

@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

try:
    data = load_data()

    with st.form("predict_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 17, 90, 30)
            workclass = st.selectbox("Workclass", sorted(data['workclass'].dropna().unique()))
            education_num = st.number_input("Education Num", 1, 16, 10)
            marital_status = st.selectbox("Marital Status", sorted(data['marital-status'].dropna().unique()))
            occupation = st.selectbox("Occupation", sorted(data['occupation'].dropna().unique()))
            relationship = st.selectbox("Relationship", sorted(data['relationship'].dropna().unique()))
        with col2:
            race = st.selectbox("Race", sorted(data['race'].dropna().unique()))
            sex = st.radio("Sex", sorted(data['sex'].dropna().unique()))
            capital_gain = st.number_input("Capital Gain", 0, 100000, 0)
            capital_loss = st.number_input("Capital Loss", 0, 5000, 0)
            hours_per_week = st.number_input("Hours per Week", 1, 99, 40)
            native_country = st.selectbox("Native Country", sorted(data['native-country'].dropna().unique()))

        submitted = st.form_submit_button("Predict")

    if submitted:
        payload = {
            "age": age, 
            "workclass": workclass, 
            "education-num": education_num, 
            "marital-status": marital_status,
            "occupation": occupation, 
            "relationship": relationship, 
            "race": race,
            "sex": sex, 
            "capital-gain": capital_gain, 
            "capital-loss": capital_loss,
            "hours-per-week": hours_per_week, 
            "native-country": native_country
        }
        try:
            response = requests.post("http://127.0.0.1:5000/predict", json=payload)
            result = response.json()
            if "error" in result:
                st.error(result["error"])
            else:
                st.success(f"Prediction: {result['prediction']}")
                st.info(f"Probability of earning >50K: {result['probability']*100:.1f}%")
        except Exception as e:
            st.error(f"Could not connect to Flask backend: {e}")

except Exception as e:
    st.error(f"تعذر تحميل ملف census.csv: {e}")