from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from agents.search import SearchAgent
from agents.verifier import VerifierAgent
from agents.trust_scorer import TrustScorerAgent
from agents.human_check import HumanCheckAgent
from agents.scraper import ScraperAgent
from pydantic import BaseModel
from typing import List, Optional
import datetime

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
    log_step('search_results', search_results)
    log_step('text_chunks', search_results)

    # Verifica la correttezza dei risultati di SearchAgent
    checked_data = verified_data = await VerifierAgent().run(search_results)
    log_step('verified_data', verified_data)

    # 4. Calcolo score
    score, details = await TrustScorerAgent().run(verified_data)
    details = {'comment': details}
    log_step('score', score)
    log_step('details', details)

    # 5. Generazione report
    report = f"""# Trust.me Report\n\n**Score di fiducia:** {score}/100\n\n## Dettagli\n{details}\n\n---\n\n## Dati analizzati\n{checked_data}\n"""
    log_step('report', report)

    return AnalysisResponse(trust_score=score, report=report, details=details)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def main_page():
    return RedirectResponse(url='/health', status_code=301)

def log_step(step, data):
    with open('debug_analyze.log', 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.datetime.now()}] {step}: {repr(data)}\n")