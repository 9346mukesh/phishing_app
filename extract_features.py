# ✅ Step 3: Feature extractor (same as your extract_features.py)
import re
import socket
import urllib.parse
import tldextract

def extract_features_from_url(url):
    features = []
    try:
        ip_match = re.search(r"(([0-9]{1,3}\.){3}[0-9]{1,3})", url)
        features.append(-1 if ip_match else 1)
        features.append(-1 if len(url) >= 75 else (0 if len(url) >= 54 else 1))
        shortening_services = r"bit\.ly|goo\.gl|tinyurl|ow\.ly|t\.co|is\.gd|cli\.gs"
        features.append(-1 if re.search(shortening_services, url) else 1)
        features.append(-1 if "@" in url else 1)
        features.append(-1 if url.count('//') > 1 else 1)
        domain = urllib.parse.urlparse(url).netloc
        features.append(-1 if '-' in domain else 1)
        subdomain = tldextract.extract(url).subdomain
        num_dots = subdomain.count('.') + 1 if subdomain else 0
        if num_dots == 0: features.append(1)
        elif num_dots == 1: features.append(0)
        else: features.append(-1)
        features.append(-1 if 'https' in domain.lower() else 1)
        features.append(1 if url.startswith('https://') else -1)
        features.append(0)  # placeholder features
        features.append(0)
        features.append(0)
        features.append(-1 if re.search(r"mailto:", url) else 1)
        features.append(0)
        features.append(0)
        features.append(-1)
        try:
            socket.gethostbyname(domain)
            features.append(1)
        except:
            features.append(-1)
        features.extend([0] * (30 - len(features)))  # pad to 30
    except Exception as e:
        features = [0]*30
    return features