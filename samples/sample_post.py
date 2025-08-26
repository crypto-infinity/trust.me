import requests
import json
import os

URL = "http://localhost:8000/analyze"

if os.path.exists("./query.json"):
    with open("query.json", "r") as f:
        data = json.load(f)
else:
    raise Exception("Query file not found.")

try:
    response = requests.post(URL, json=data).json()
    
    print(f"""Your check for {data["subject"]}:\nTrust Score: {response["trust_score"]}\nDetails: {response["details"]["comment"]}""")

except Exception as e:
    print(e)

### Pydantic Data structures

# class AnalysisRequest(BaseModel):
#     subject: str # Person or company name
#     type: str  # "person" | "company"
#     context: str # "search context"

# class AnalysisResponse(BaseModel):
#     trust_score: float
#     report: str
#     details: dict