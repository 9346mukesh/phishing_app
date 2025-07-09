import joblib
from extract_features import extract_features_from_url

# Load model and scaler
model = joblib.load("phishing_rf_model.pkl")
scaler = joblib.load("scaler.pkl")

# Sample test URL (phishing example)
url = "http://secure-login.bit.ly/update-info"

# Extract features from the URL
features = extract_features_from_url(url)
print("Extracted features:", features)

# Scale and predict
scaled = scaler.transform([features])
prediction = model.predict(scaled)[0]

# Display result
result = "✅ Legitimate" if prediction == 0 else "🚨 Phishing"
print("Prediction:", result)
