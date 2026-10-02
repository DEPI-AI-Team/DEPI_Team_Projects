import streamlit as st

st.set_page_config(page_title="CharityML Dashboard", page_icon="💰", layout="wide")

st.title("💰 CharityML — Finding Donors Dashboard")
st.markdown("""
Welcome! Use the sidebar to navigate:
- **Data Overview**: explore the census dataset
- **Visualizations**: see feature distributions
- **Predict**: estimate if a person earns more than $50K
""")