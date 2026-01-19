"""Streamlit web UI for phishing detection - Modern Redesigned."""

import os
from datetime import datetime

import requests
import streamlit as st

from src.phishing.utils.logging_config import get_logger
from src.phishing.utils.validators import URLValidationError, validate_url

logger = get_logger("streamlit_ui")

# Page configuration
st.set_page_config(
    page_title="🛡️ Phishing Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern design
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif !important;
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }

    .main-header h1 {
        color: white !important;
        font-size: 2.5rem !important;
        margin: 0 !important;
        font-weight: 700 !important;
    }

    .main-header p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
    }

    .result-box {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        border: 2px solid #E5E7EB;
        transition: all 0.3s ease;
    }

    .result-box.phishing {
        border-color: #EF4444;
        background: rgba(239, 68, 68, 0.05);
    }

    .result-box.legitimate {
        border-color: #10B981;
        background: rgba(16, 185, 129, 0.05);
    }

    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3) !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 2px solid #E5E7EB !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    .stSidebar {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    .stSidebar [data-testid="stMarkdownContainer"] {
        color: white !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# API configuration
# Prefer Streamlit secrets in cloud, fall back to environment/local default
API_URL = os.getenv("API_URL") or st.secrets.get("API_URL", "http://localhost:8000")


def get_api_health():
    """Check API health."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False


def predict_url(url: str):
    """Get prediction from API."""
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={"url": url},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Prediction failed")}
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return {"error": f"API Error: {str(e)}"}


def predict_batch(urls: list):
    """Get batch predictions from API."""
    try:
        response = requests.post(
            f"{API_URL}/predict-batch",
            json={"urls": urls},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Batch prediction failed")}
    except requests.exceptions.RequestException as e:
        logger.error(f"Batch API request failed: {str(e)}")
        return {"error": f"API Error: {str(e)}"}


# Sidebar
with st.sidebar:
    st.markdown(
        "<h2 style='color: white; font-weight: 700; margin-bottom: 1.5rem;'>⚙️ Settings</h2>",
        unsafe_allow_html=True,
    )

    api_status = get_api_health()

    if api_status:
        st.success("🟢 **API Status:** Connected", icon="✅")
    else:
        st.error("🔴 **API Status:** Disconnected", icon="❌")

    st.divider()

    mode = st.radio(
        "📋 Select Mode:",
        ["🔍 Single URL Analysis", "📦 Batch Analysis"],
        help="Analyze one URL or multiple URLs at once",
    )

    st.divider()

    with st.expander("📖 How to Use", expanded=False):
        st.markdown(
            """
        **Single URL Mode:**
        - Enter any website URL
        - Get instant phishing detection
        - View confidence score

        **Batch Mode:**
        - Paste multiple URLs
        - Analyze up to 100 URLs

        **Risk Levels:**
        - 🟢 Low Risk: Legitimate
        - 🔴 High Risk: Phishing
        """
        )

# Main content
st.markdown(
    """
    <div class='main-header'>
        <h1>🛡️ Advanced Phishing Website Detector</h1>
        <p>Real-time ML-powered URL analysis for phishing threats</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not api_status:
    st.error(f"❌ **API Service Unavailable** - Cannot connect to {API_URL}", icon="🚨")
else:
    if "🔍 Single URL Analysis" in mode:
        # Single URL analysis
        st.markdown("### 🔍 Analyze Single URL")

        col1, col2 = st.columns([4, 1])

        with col1:
            url_input = st.text_input(
                "Enter URL to analyze:",
                placeholder="https://example.com",
                help="Full URL with protocol (http:// or https://)",
            )

        with col2:
            analyze_button = st.button("🔍 Analyze", use_container_width=True)

        if analyze_button and url_input:
            with st.spinner("🔄 Analyzing URL..."):
                try:
                    validated_url = validate_url(url_input)
                    result = predict_url(validated_url)

                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        is_phishing = result.get("prediction") == 1
                        confidence = result.get("confidence", 0)

                        if is_phishing:
                            st.markdown(
                                """
                                <div class='result-box phishing'>
                                    <h2 style='color: #EF4444; margin: 0;'>
                                        🚨 PHISHING DETECTED
                                    </h2>
                                    <p style='color: #7F1D1D; margin: 0.5rem 0 0 0;'>
                                        This URL shows characteristics of a phishing site
                                    </p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                """
                                <div class='result-box legitimate'>
                                    <h2 style='color: #10B981; margin: 0;'>
                                        ✅ LEGITIMATE SITE
                                    </h2>
                                    <p style='color: #065F46; margin: 0.5rem 0 0 0;'>
                                        This URL appears to be safe
                                    </p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        st.divider()
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("🎯 Prediction", result.get("label", "Unknown"))

                        with col2:
                            st.metric("📊 Confidence", f"{confidence:.1%}")

                        with col3:
                            risk_level = "🔴 High Risk" if is_phishing else "🟢 Low Risk"
                            st.metric("⚠️ Risk Level", risk_level)

                        st.divider()

                        with st.expander("📊 Detailed Analysis", expanded=True):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown("**Analysis Details:**")
                                st.markdown(
                                    f"""
                                - **URL**: `{result.get('url', 'N/A')}`
                                - **Prediction**: {result.get('label', 'N/A')}
                                - **Confidence**: {confidence:.2%}
                                - **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                                """
                                )

                            with col2:
                                st.markdown("**What This Means:**")
                                if is_phishing:
                                    st.markdown(
                                        """
                                    ⚠️ **Phishing Alert**

                                    Suspicious characteristics detected
                                    """
                                    )
                                else:
                                    st.markdown(
                                        """
                                    ✅ **Safe URL**

                                    Appears legitimate based on analysis
                                    """
                                    )

                except URLValidationError as e:
                    st.error(f"❌ Invalid URL: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")

        st.divider()
        st.markdown("### 🧪 Quick Test Examples")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**✅ Legitimate Sites:**")
            for url in ["https://www.google.com", "https://github.com"]:
                if st.button(f"📌 {url}", key=f"legit_{url}"):
                    st.session_state.url = url

        with col2:
            st.markdown("**🚨 Suspicious Sites:**")
            for url in ["https://bit.ly/fake", "https://paypal-verify.tk"]:
                if st.button(f"📌 {url}", key=f"phish_{url}"):
                    st.session_state.url = url

    else:
        # Batch analysis
        st.markdown("### 📦 Batch URL Analysis")

        batch_input = st.text_area(
            "Enter URLs (one per line):",
            placeholder="https://example1.com\nhttps://example2.com",
            height=250,
        )

        col1, col2 = st.columns(2)
        with col1:
            analyze_batch_button = st.button("🔍 Analyze Batch", use_container_width=True)
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)

        if clear_button:
            batch_input = ""

        if analyze_batch_button and batch_input:
            urls = [u.strip() for u in batch_input.strip().split("\n") if u.strip()]

            if len(urls) == 0:
                st.warning("⚠️ No URLs provided")
            elif len(urls) > 100:
                st.error(f"❌ Too many URLs. Maximum 100 allowed, got {len(urls)}")
            else:
                with st.spinner(f"🔄 Analyzing {len(urls)} URLs..."):
                    try:
                        result = predict_batch(urls)

                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            col1, col2, col3, col4 = st.columns(4)

                            total = len(urls)
                            phishing_count = sum(
                                1 for r in result.get("results", []) if r.get("prediction") == 1
                            )
                            legitimate_count = total - phishing_count
                            risk_pct = (phishing_count / total * 100) if total > 0 else 0

                            with col1:
                                st.metric("📊 Total URLs", total)
                            with col2:
                                st.metric("🚨 Phishing", phishing_count)
                            with col3:
                                st.metric("✅ Legitimate", legitimate_count)
                            with col4:
                                st.metric("⚠️ Risk %", f"{risk_pct:.1f}%")

                            st.divider()

                            if result.get("results"):
                                st.markdown("### 📊 Detailed Results")

                                phishing = [
                                    r for r in result["results"] if r.get("prediction") == 1
                                ]
                                legitimate = [
                                    r for r in result["results"] if r.get("prediction") == 0
                                ]

                                if phishing:
                                    st.markdown(f"#### 🚨 Phishing URLs ({len(phishing)})")
                                    for item in phishing:
                                        col1, col2 = st.columns([3, 1])
                                        with col1:
                                            st.markdown(f"🔴 `{item['url']}`")
                                        with col2:
                                            st.markdown(f"**{item.get('confidence', 0):.1%}**")

                                if legitimate:
                                    st.markdown(f"#### ✅ Legitimate URLs ({len(legitimate)})")
                                    for item in legitimate:
                                        col1, col2 = st.columns([3, 1])
                                        with col1:
                                            st.markdown(f"🟢 `{item['url']}`")
                                        with col2:
                                            st.markdown(f"**{item.get('confidence', 0):.1%}**")

                    except Exception as e:
                        st.error(f"❌ Batch analysis failed: {str(e)}")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; margin-top: 2rem;'>
    <p style='color: #6B7280; font-size: 0.9rem;'>
    🛡️ Phishing Detector v1.0.0 | Accuracy: 89.78% | ⚠️ Educational Use Only
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)
