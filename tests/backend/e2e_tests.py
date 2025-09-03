
import requests
import json


def test_analyze_method(url="http://localhost:8000/analyze"):

    with open("query.json", "r") as f:
        data = json.load(f)

    assert data is not None, "File query.json not loaded."

    resp = requests.post(url, json=data)
    assert resp.status_code == 200, (
        f"Analyze method failed, got response {resp.status_code}"
    )

    print(resp.json())
