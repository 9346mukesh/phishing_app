import streamlit as st
import joblib
import numpy as np
from extract_features import extract_features_from_url  # or define inline

# Load model and scaler
model = joblib.load("phishing_rf_model.pkl")
scaler = joblib.load("scaler.pkl")

st.set_page_config(page_title="Phishing Detector")
st.title("🔐 Phishing Website Detector")

# URL Input
url = st.text_input("🔗 Enter a website URL:")

if st.button("Analyze"):
    try:
        # Extract features from URL
        features = extract_features_from_url(url)
        scaled = scaler.transform([features])
        prediction = model.predict(scaled)[0]
        label = "✅ Legitimate" if prediction == 0 else "🚨 Phishing"
        st.success(f"Prediction: {label}")
    except Exception as e:
        st.error(f"Error: {e}")