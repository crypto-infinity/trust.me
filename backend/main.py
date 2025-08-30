#Load env variables
from dotenv import load_dotenv
load_dotenv()

#Load fastapi
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

#Load agents
from agents.search import SearchAgent
from agents.verifier import VerifierAgent
from agents.trust_scorer import TrustScorerAgent
from agents.scraper import ScraperAgent

#Load data structures
from pydantic import BaseModel
from collections import defaultdict

#FastAPI Setup
app = FastAPI(title="Trust.me API")

# Google search parameters
params = {
    "location": "United States",
    "device": "desktop",
    "hl": "en",
    "gl": "us",
    "num": 10
}

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Data structures setup
class AnalysisRequest(BaseModel):
    subject: str # Person or company name, mandatory
    context: str # "search context"

class AnalysisResponse(BaseModel):
    trust_score: float #score assigned by the LLM
    details: str #string representing the LLM details based on search results

# POST /analyze
# curl -X POST http://localhost:8000/analyze \
#   -H "Content-Type: application/json" \
#   -d '{
#     "subject": "John Doe",
#     "context": "Verifica affidabilità per collaborazione aziendale"
#   }'

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):

    #Variables setup
    checked = False
    query = ""
    checked_data = None
    score = 0
    details = None

    #Verification log
    verification_log = defaultdict(list)
    verification_log['searches'] = []
    verification_log['whys'] = []

    try:
        while(not checked):

            search_results = ""

            print("Beginning SerpAPI Searches.")

            # 1 Search links through SerpAPI
            search_results = await SearchAgent().run(
                request.subject, 
                request.context, 
                query, 
                params
            )

            print("Beginning Scraping and Preprocessing.")

            # 2 Web Scraping, embeddings and preprocessing
            scraped_data = await ScraperAgent().run(
                search_results,
                request.subject + request.context + query #for similarity search
            )

            print("Beginning Validation.")

            # 3 Relevant chunks verification through automatic validation
            checked_data = await VerifierAgent().run(scraped_data)

            # Check if VerifierAgent gives ok, otherwise append motivations and reiterate
            if(checked_data['verified'] == "OK"): 
                checked = True
                verification_log["searches"].append(checked_data['data'])
            else:
                verification_log['searches'].append(checked_data['data'])
                verification_log['whys'].append(checked_data['error_details']['whys'])

                query = checked_data['error_details']['suggested_retry']

        print("Beginning Scoring.")

        # 4. Score computing
        score, details = await TrustScorerAgent().run(verification_log)

        if not details or not score: raise Exception("LLM Parsing Failed.")
    
    except HTTPException as httpexc:
        print(httpexc)
        raise HTTPException(status_code=500, detail=str(httpexc))

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    print("Analysis complete!")
    # 5. Return data
    return AnalysisResponse(trust_score=score or 0.0, details=details or "")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def main_page():
    return RedirectResponse(url='/health', status_code=301)