import os
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Predict")
st.title("🔮 Predict Income")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, 'census.csv')

@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

data = load_data()

with st.form("predict_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 17, 90, 30)
        workclass = st.selectbox("Workclass", sorted(data['workclass'].unique()))
        education_level = st.selectbox("Education Level", sorted(data['education_level'].unique()))
        education_num = st.number_input("Education Num", 1, 16, 10)
        marital_status = st.selectbox("Marital Status", sorted(data['marital-status'].unique()))
        occupation = st.selectbox("Occupation", sorted(data['occupation'].unique()))
        relationship = st.selectbox("Relationship", sorted(data['relationship'].unique()))
    with col2:
        race = st.selectbox("Race", sorted(data['race'].unique()))
        sex = st.radio("Sex", sorted(data['sex'].unique()))
        capital_gain = st.number_input("Capital Gain", 0, 100000, 0)
        capital_loss = st.number_input("Capital Loss", 0, 5000, 0)
        hours_per_week = st.number_input("Hours per Week", 1, 99, 40)
        native_country = st.selectbox("Native Country", sorted(data['native-country'].unique()))

    submitted = st.form_submit_button("Predict")

if submitted:
    payload = {
        "age": age, "workclass": workclass, "education_level": education_level,
        "education-num": education_num, "marital-status": marital_status,
        "occupation": occupation, "relationship": relationship, "race": race,
        "sex": sex, "capital-gain": capital_gain, "capital-loss": capital_loss,
        "hours-per-week": hours_per_week, "native-country": native_country
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