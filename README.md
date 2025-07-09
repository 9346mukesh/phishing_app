# 🛡️ Phishing Detection App

A machine learning-based web application built with **Streamlit** that detects whether a URL is legitimate or a phishing attempt. The app uses a trained ML model to extract features from a given URL and predict its legitimacy.

---

## 🚀 Features

- ✅ Takes a URL as input.
- 🔍 Automatically extracts relevant features from the URL.
- 🧠 Uses a trained machine learning model to classify the URL as **Legitimate** or **Phishing**.
- 🌐 Simple and interactive **Streamlit** web interface.

---

## 📁 Project Structure
phishing_app/
├── app.py                     # Streamlit app
├── model.pkl                  # Trained machine learning model
├── feature_extraction.py      # Script to extract features from URL
├── requirements.txt           # Required Python packages

---

## 🧑‍💻 How to Run the App Locally

### 🔧 1. Clone the Repository

```bash
git clone https://github.com/your-username/phishing_app.git
cd phishing_app
📦 2. Create and Activate Virtual Environment (Recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
3. Install Required Packages
pip install -r requirements.txt
▶️ 4. Run the Streamlit App
streamlit run app.py

🧪 Example:
Enter a URL like:http://example.com/login/secure
output:
⚠️  phishing.
