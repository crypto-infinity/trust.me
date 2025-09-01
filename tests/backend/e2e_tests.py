
import requests
import json


def test_analyze_method(url):

    with open("query.json", "r") as f:
        data = json.load(f)

    assert data is not None, "File query.json not loaded."

    response = requests.post(url, json=data).json()

    assert (
        response.status_code == 200
    ), f"Analyze method failed, got response {response.status}"

    print(
        f"Your check for {data['subject']}:\n"
        f"Trust Score: {response['trust_score']}\n"
        f"Details: {response['details']['comment']}"
    )
