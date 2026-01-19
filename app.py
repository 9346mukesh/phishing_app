"""Streamlit Cloud entrypoint.

This wrapper imports and executes the real Streamlit app at
src/phishing/ui/app.py so you can use `app.py` as the Main file path.
"""

# Ensure Streamlit is available (helps some environments detect usage)
import streamlit as _st  # noqa: F401

# Importing this module executes the Streamlit UI code.
import src.phishing.ui.app  # noqa: F401
