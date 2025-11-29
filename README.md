## 🛡️ Phishing Website Detection App
A robust Machine Learning application designed to identify and classify phishing URLs in real-time using Random Forest algorithms and lexical feature extraction.

## 📖 Overview
In the evolving landscape of cybersecurity, phishing remains one of the most prevalent threats. This project automates the detection of malicious websites by analyzing the structural and lexical components of a URL.

The application leverages a pre-trained Random Forest Classifier to evaluate URLs against a set of engineered features (such as length, presence of IP addresses, and shortening services). It is wrapped in a lightweight Streamlit interface, making it accessible for non-technical users to verify links instantly.

## 🚀 Key Features
Real-time Analysis: Instant classification of URLs as "Legitimate" or "Phishing".

Feature Engineering: Automatically extracts 30 distinct features from the input URL, including domain age, protocol analysis, and special character usage.

ML-Powered: Utilizes a Random Forest model (Accuracy ~95.2%) for robust prediction.

Live DNS Check: Validates the existence of the domain using socket connections.

Interactive UI: Clean, web-based user interface built with Streamlit.

## 🏗️ System Architecture
The data flow follows a standard Machine Learning pipeline: Input → Extraction → Scaling → Inference → Output.


    graph LR
    A[User Input URL] --> B[Feature Extractor]
    B -->|Lexical & DNS Analysis| C[Feature Vector (1x30)]
    C --> D[Standard Scaler]
    D -->|Normalized Data| E[Random Forest Model]
    E --> F{Prediction}
    F -->|0| G[✅ Legitimate]
    F -->|1| H[🚨 Phishing]
## 🔬 Algorithm & Logic
The core intelligence lies in extract_features.py. The model does not read the website content (HTML); instead, it analyzes the URL string itself.

Feature Extraction Strategy
The system extracts a feature vector containing 30 data points. Key heuristics include:

IP Address Check: Phishing sites often use IP addresses instead of domain names.

URL Length: Long URLs (>= 54 chars) are flagged as suspicious; extremely long URLs (>= 75) are high risk.

Shortening Services: Checks against a blacklist of shorteners (bit.ly, tinyurl, etc.) often used to hide malicious links.

Special Characters: Presence of @ (ignoring browser credentials) or multiple slashes //.

Subdomain Depth: Counts the number of dots in the subdomain.

Protocol: Checks for https usage and verifies if https token is deceptively used in the domain name.

DNS Validation: Uses socket.gethostbyname to verify the domain actually resolves.

Note: The feature vector is padded to a length of 30 to ensure compatibility with the input shape required by the trained Random Forest model.

## 🛠️ Tech Stack
    | Component        | Technology              | Purpose                              |
    |------------------|--------------------------|--------------------------------------|
    | Language         | Python                   | Core logic and scripting             |
    | Frontend         | Streamlit                | Web application interface            |
    | ML Engine        | Scikit-Learn             | Random Forest implementation         |
    | Data Processing  | Pandas / NumPy           | Array manipulation                   |
    | Serialization    | Joblib                   | Loading trained models (.pkl)        |
    | Networking       | Tldextract / Socket      | Domain parsing and DNS validation    |

## 📂 Project Structure
Bash
 
    phishing_app/
    ├── app.py                     # Main Streamlit application entry point
    ├── extract_features.py        # Core logic for feature extraction from URLs
    ├── test_model.py              # CLI script for testing predictions manually
    ├── phishing_rf_model.pkl      # Pre-trained Random Forest Classifier
    ├── scaler.pkl                 # Pre-fitted Standard Scaler for normalization
    ├── phishing_dataset.csv       # Dataset used for training/validation
    ├── requirements.txt           # Project dependencies
    ├── ppt.pptx                   # Project presentation and documentation
    └── README.md                  # Project documentation
## ⚙️ Installation & Setup
Follow these steps to set up the project locally.

1. Clone the Repository

       git clone https://github.com/your-username/phishing_app.git
       cd phishing_app
2. Create Virtual Environment (Recommended)
Bash

       python -m venv venv
  # Windows
       venv\Scripts\activate
# Mac/Linux
      source venv/bin/activate
3. Install Dependencies
    Bash

       pip install -r requirements.txt
## 🖥️ Usage
Running the Web App
To launch the interactive dashboard:

Bash

     streamlit run app.py
The app will open in your default browser at http://localhost:8501.

Running via CLI
To test a specific URL without the UI:

       Open test_model.py.

Edit the url variable.

Run:

Bash

     python test_model.py
Sample Output:

Plaintext

Extracted features: [1, -1, 1, 1, 1, 1, 0, 1, -1, 0, 0, 0, 1, ...]
Prediction: 🚨 Phishing
## 📊 Dataset & Performance
The model was trained on a balanced dataset containing legitimate and phishing URLs.

Dataset Source: phishing_dataset.csv (Mixed sources including OpenPhish and PhishTank).

Labels:

0: Legitimate Website

1: Phishing Website

Model Performance:

Accuracy: ~95.2%

Precision/Recall: High precision in detecting deceptive shortening services.

## 🔮 Future Enhancements
Content-Based Analysis: Implement HTML scraping (BeautifulSoup) to analyze page content and forms.

WHOIS Integration: Check domain registration date (newly created domains are often malicious).

API Development: Migrate the backend to Flask/FastAPI to expose the detection engine as a REST API.

Deep Learning: Experiment with CNNs or RNNs for character-level URL analysis.

## 👥 Contributors
Mukesh Kumar Reddy - Team Lead & ML Engineer

Yogeswar - Data Analysis

Pranav - Backend Logic
