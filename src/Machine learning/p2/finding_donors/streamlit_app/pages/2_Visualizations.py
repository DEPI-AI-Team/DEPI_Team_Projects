import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Visualizations")
st.title("📈 Visualizations")

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

    if 'education_level' in data.columns:
        st.subheader("Education Level vs Income")
        edu_income = pd.crosstab(data['education_level'], data['income'])
        st.bar_chart(edu_income)
except Exception as e:
    st.error(f"تعذر تحميل البيانات: {e}")