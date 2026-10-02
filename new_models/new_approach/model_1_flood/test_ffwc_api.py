import requests
import re

url = "http://ffwc.gov.bd/main.2152bfd7eac61673.js"
r = requests.get(url, timeout=10)

# Search for paths starting with https://api.ffwc.gov.bd or /api/
matches = re.findall(r'https://api\.ffwc\.gov\.bd/[a-zA-Z0-9_\-/]+', r.text)
print("FFWC API Paths found:", set(matches))

# Also search for 'Bahadurabad' or station IDs in JS text
if "Bahadurabad" in r.text or "46.9" in r.text:
    print("Bahadurabad reference found in main bundle!")
