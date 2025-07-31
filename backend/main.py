from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.search import SearchAgent
from agents.verifier import VerifierAgent
from agents.trust_scorer import TrustScorerAgent
from agents.human_check import HumanCheckAgent
from agents.report import ReportAgent
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Trust.me - Backend API")

# CORS setup (modifica origins in base al frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    subject: str
    type: str  # "person" | "company"
    context: Optional[str] = None

class AnalysisResponse(BaseModel):
    trust_score: float
    report: str
    details: dict

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    # 1. Ricerca profili pubblici
    search_results = await SearchAgent().run(request.subject, request.type)
    # 2. Verifica e validazione (usa direttamente i risultati della ricerca)
    verified_data = await VerifierAgent().run(search_results)
    # 3. Calcolo score
    score, details = await TrustScorerAgent().run(verified_data)
    # 4. Check umano (opzionale)
    checked_data = await HumanCheckAgent().run(verified_data)
    # 5. Generazione report
    report = await ReportAgent().run(checked_data, score, details)
    return AnalysisResponse(trust_score=score, report=report, details=details)

@app.get("/health")
def health():
    return {"status": "ok"}
