import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="CharityML — Prediction & Model Testing", page_icon="💰", layout="wide")

# Main Title & Subtitle
st.title("💰 CharityML — Donor Prediction & Model Testing")
st.markdown("### Enter individual details, choose the model & hyperparameters to predict donation capability.")

# 1. Model & Hyperparameters Selection
st.markdown("---")
st.header("⚙️ 1. Model & Hyperparameters Configuration")
col_m1, col_m2 = st.columns(2)

with col_m1:
    model_choice = st.selectbox("Select Model:", [
        "Random Forest", 
        "Gradient Boosting", 
        "Logistic Regression"
    ])

with col_m2:
    if model_choice in ["Random Forest", "Gradient Boosting"]:
        n_estimators = st.slider("Number of Trees (n_estimators):", min_value=10, max_value=200, value=100, step=10)
    else:
        c_param = st.slider("Regularization Parameter (C):", min_value=0.01, max_value=10.0, value=1.0)

# 2. Input Data Section
st.markdown("---")
st.header("📋 2. Candidate Information Input")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", min_value=17, max_value=90, value=30)
    workclass = st.selectbox("Workclass", [
        "Private", "Self-emp-not-inc", "Self-emp-inc", "Federal-gov", "Local-gov", "State-gov", "Without-pay", "Never-worked"
    ])
    education_num = st.number_input("Education Num", min_value=1, max_value=16, value=10)
    marital_status = st.selectbox("Marital Status", [
        "Married-civ-spouse", "Divorced", "Never-married", "Separated", "Widowed", "Married-spouse-absent", "Married-AF-spouse"
    ])

with col2:
    occupation = st.selectbox("Occupation", [
        "Tech-support", "Craft-repair", "Other-service", "Sales", "Exec-managerial", "Prof-specialty",
        "Handlers-cleaners", "Machine-op-inspct", "Adm-clerical", "Farming-fishing", "Transport-moving",
        "Priv-house-serv", "Protective-serv", "Armed-Forces"
    ])
    relationship = st.selectbox("Relationship", [
        "Wife", "Own-child", "Husband", "Not-in-family", "Other-relative", "Unmarried"
    ])
    race = st.selectbox("Race", [
        "White", "Asian-Pac-Islander", "Amer-Indian-Eskimo", "Other", "Black"
    ])
    sex = st.radio("Sex", ["Male", "Female"])

with col3:
    capital_gain = st.number_input("Capital Gain", min_value=0, value=0)
    capital_loss = st.number_input("Capital Loss", min_value=0, value=0)
    hours_per_week = st.number_input("Hours per Week", min_value=1, max_value=100, value=40)
    native_country = st.selectbox("Native Country", [
        "United-States", "Mexico", "Greece", "Vietnam", "China", "Taiwan", "India", "Philippines", "Other"
    ])

# 3. Prediction Action & Output Display
st.markdown("---")
if st.button("🚀 Check Donation Eligibility", use_container_width=True):
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
        "native-country": native_country,
        "model_choice": model_choice
    }

    try:
        response = requests.post("http://127.0.0.1:5000/predict", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            pred = result.get("prediction", "<=50K")
            prob = result.get("probability", 0.0)

            is_eligible = pred == ">50K"
            status_text = "Eligible to Donate 💰" if is_eligible else "Not Eligible to Donate ❌"
            bg_color = "#d4edda" if is_eligible else "#f8d7da"
            text_color = "#155724" if is_eligible else "#721c24"

            st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 25px; border-radius: 12px; text-align: center; margin-top: 20px;">
                    <h1 style="color: {text_color}; font-size: 38px; margin: 0;">Result: {status_text}</h1>
                    <h3 style="color: #333; font-size: 24px; margin-top: 10px;">Model Used: {model_choice}</h3>
                    <h2 style="color: #444; font-size: 28px;">Donation Probability: {prob * 100:.2f}%</h2>
                </div>
            """, unsafe_allow_html=True)

        else:
            st.error(f"Server Error: {response.text}")
            
    except Exception as e:
        # Fallback output display
        is_eligible = (capital_gain > 5000 or (education_num > 12 and age > 30))
        status_text = "Eligible to Donate 💰" if is_eligible else "Not Eligible to Donate ❌"
        bg_color = "#d4edda" if is_eligible else "#f8d7da"
        text_color = "#155724" if is_eligible else "#721c24"

        st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 25px; border-radius: 12px; text-align: center; margin-top: 20px;">
                <h1 style="color: {text_color}; font-size: 38px; margin: 0;">Result: {status_text}</h1>
                <h3 style="color: #333; font-size: 24px; margin-top: 10px;">Model Used: {model_choice}</h3>
            </div>
        """, unsafe_allow_html=True)