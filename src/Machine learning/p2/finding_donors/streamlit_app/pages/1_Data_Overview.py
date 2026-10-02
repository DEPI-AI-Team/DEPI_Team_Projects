import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Overview")
st.title("📊 Census Data Overview")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, 'census.csv')

@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

data = load_data()

col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(data))
col2.metric("Earning >50K", (data['income'] == '>50K').sum())
col3.metric("Earning <=50K", (data['income'] == '<=50K').sum())

st.subheader("Income Distribution")
st.bar_chart(data['income'].value_counts())

st.subheader("Sample Data")
st.dataframe(data.head(20))