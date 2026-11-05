import os
import requests
import json

API_URL = os.getenv("API_URL", "http://localhost:8000")

def seed():
    print(f"Connecting to API at: {API_URL}")
    seed_endpoint = f"{API_URL.rstrip('/')}/products/seed"
    try:
        response = requests.post(seed_endpoint, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("Success! Database populated:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == "__main__":
    seed()
