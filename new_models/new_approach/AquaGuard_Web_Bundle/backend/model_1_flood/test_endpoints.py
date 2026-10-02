import requests

endpoints = [
    "https://api.ffwc.gov.bd/api/v1/waterlevels",
    "https://api.ffwc.gov.bd/api/v1/stations",
    "https://api.ffwc.gov.bd/waterlevel",
    "https://api.ffwc.gov.bd/stations",
    "http://ffwc.gov.bd/ffwc_app/waterlevel",
    "http://ffwc.gov.bd/json/wl.json"
]

for ep in endpoints:
    try:
        r = requests.get(ep, timeout=5)
        print(f"{ep} -> Code: {r.status_code}, Length: {len(r.text)}")
        if r.status_code == 200:
            print("Response:", r.text[:200])
    except Exception as e:
        print(f"{ep} -> Error: {e}")
