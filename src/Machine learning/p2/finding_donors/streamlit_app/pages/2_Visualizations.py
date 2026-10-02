import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Visualizations")
st.title("📈 Visualizations")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, 'census.csv')

@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

data = load_data()

st.subheader("Capital Gain Distribution (Skewed)")
fig, ax = plt.subplots()
data['capital-gain'].hist(bins=30, ax=ax)
st.pyplot(fig)

st.subheader("Age Distribution by Income")
fig2, ax2 = plt.subplots()
data[data['income'] == '>50K']['age'].hist(bins=20, alpha=0.6, label='>50K', ax=ax2)
data[data['income'] == '<=50K']['age'].hist(bins=20, alpha=0.6, label='<=50K', ax=ax2)
ax2.legend()
st.pyplot(fig2)

st.subheader("Education Level vs Income")
edu_income = pd.crosstab(data['education_level'], data['income'])
st.bar_chart(edu_income)