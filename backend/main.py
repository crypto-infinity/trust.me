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
    subject: str # Person or company name
    type: str  # "person" | "company"
    context: str # "search context"

class AnalysisResponse(BaseModel):
    trust_score: float
    report: str
    details: dict

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):

    checked = False
    new_suggested_query = "social profile linkedin crunchbase"
    checked_data = None

    #Verification log
    verification_log = {}
    verification_log['whys'] = []
    verification_log['searches'] = []

    try:

        while(not checked):

            search_results = ""

            # 1 OSINT info
            search_results = await SearchAgent().run(request.subject, request.context, new_suggested_query)
            log_step('search_results', search_results)

            # 2 Web Scraping
            scraped_data = await ScraperAgent().run(search_results)
            log_step('scraped_data', search_results)

            # 3 Verification through automatic info validation
            checked_data = await VerifierAgent().run(scraped_data)
            log_step('verified_data', checked_data)

            if(checked_data['verified'] == "OK"): 
                checked = True
                if checked_data['data'] == "" or checked_data['data'] == None: checked_data['data'] = str(search_results)
            else:
                #in-progress: append all results during validation phase
                
                verification_log['searches'].append(checked_data['data'])#testare
                verification_log['whys'].append(checked_data['error_details']['whys'])

                new_suggested_query = checked_data['error_details']['suggested_retry']
        
        # 4. Calcolo score
        score, details = await TrustScorerAgent().run(str(verification_log)) #modificare e testare
        details = {'comment': details}
        log_step('score', score)
        log_step('details', details)
    
    except IOError as ioerr:
        print(ioerr)

    except Exception as e:
        print(e)

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