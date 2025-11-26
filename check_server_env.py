"""Check what environment variables the server actually sees."""

import requests
import json

# Add a debug endpoint to check env vars
print("Testing server environment variables...")

response = requests.get("http://localhost:8000/system/info", headers={"x-internal-key": "ALIINSIDER-2025"})

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))
else:
    print(f"Failed: {response.status_code}")
    print(response.text)
