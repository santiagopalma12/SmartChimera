import requests
import json

print("Enviando request a http://localhost:8000/api/recommend...")

payload = {
    "mission_profile": "innovacion",
    "min_size": 3,
    "max_size": 5,
    "required_skills": ["Python", "React"]
}

try:
    response = requests.post(
        "http://localhost:8000/api/recommend",
        json=payload,
        timeout=10
    )
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"\nError en el request: {e}")
