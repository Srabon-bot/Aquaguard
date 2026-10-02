import requests
import re

url = "http://ffwc.gov.bd/"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

# Extract main JS files
js_files = re.findall(r'src=["\']([^"\']+\.js)["\']', r.text)
print("JS Files found:", js_files)

for js in js_files:
    if js.startswith("http"):
        js_url = js
    else:
        js_url = "http://ffwc.gov.bd/" + js.lstrip('/')
        
    try:
        r_js = requests.get(js_url, timeout=10)
        # Search for API URLs
        urls = re.findall(r'https?://[a-zA-Z0-9\.\-_/:\?=\&\+]+', r_js.text)
        ffwc_api = [u for u in urls if 'ffwc' in u.lower() or 'api' in u.lower() or 'water' in u.lower()]
        print(f"\nJS File: {js}")
        print("Found API Endpoints:", set(ffwc_api[:15]))
    except Exception as e:
        print(f"Error fetching {js}: {e}")
