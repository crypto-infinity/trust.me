
"""
Main FastAPI application for Trust.me API.
"""
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from agents.search import SearchAgent
from agents.verifier import VerifierAgent
from agents.scorer import ScorerAgent
from agents.scraper import ScraperAgent
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from pydantic import BaseModel, AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from collections import defaultdict
import logging

from config import __VERSION__, __DEBUG_LEVEL__, __N_VALIDATION_RETRIES__

# Load env variables
load_dotenv()

logging.basicConfig(
    level=__DEBUG_LEVEL__, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = ['http://localhost:8000']
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""
    TENANT_ID: str = ""
    SCOPE_DESCRIPTION: str = "user_impersonation"

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True,
        extra = "allow"

    @computed_field
    @property
    def SCOPE_NAME(self) -> str:
        return f'api://{self.APP_CLIENT_ID}/{self.SCOPE_DESCRIPTION}'

    @computed_field
    @property
    def SCOPES(self) -> dict:
        return {
            self.SCOPE_NAME: self.SCOPE_DESCRIPTION,
        }


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Load OpenID config on startup.
    """
    await azure_scheme.openid_config.load_config()
    yield


azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.APP_CLIENT_ID,
    tenant_id=settings.TENANT_ID,
    scopes=settings.SCOPES,
    allow_guest_users=True
)


# FastAPI Setup
app = FastAPI(
    title="Trust.me API",
    version=__VERSION__,
    description=(
        "TrustMe: automatic agentic trust validation for online identities"
    ),
    swagger_ui_oauth2_redirect_url='/oauth2-redirect',
    swagger_ui_init_oauth={
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': settings.OPENAPI_CLIENT_ID,
    },
    lifespan=lifespan
)


# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Data structures setup

class AnalysisRequest(BaseModel):
    """
    Request model for analysis endpoint.
    Attributes:
        subject: Person or company name (required)
        context: Search context (required)
    """
    subject: str  # Person or company name, mandatory
    context: str  # search context
    language: str  # output language


class AnalysisResponse(BaseModel):
    """
    Response model for analysis endpoint.
    Attributes:
        trust_score: Score assigned by the LLM
        details: String representing the LLM details based on search results
    """
    trust_score: float  # score assigned by the LLM
    details: str  # string representing the LLM details based on search results


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    return await inference(request)


async def inference(request: AnalysisRequest):
    """
    Main endpoint for trust analysis.
    Orchestrates search, scraping, validation, and scoring using agent classes.
    Requires environment variables for all agent classes (see docstrings).
    Args:
        request: AnalysisRequest object containing subject and context.
    Returns:
        AnalysisResponse with trust_score and details.
    """

    logging.info("Beginning scoring of subject...")

    checked = False
    counter = 0
    checked_data = None
    score = 0
    details = None
    verification_log = defaultdict(list)
    verification_log["searches"] = []
    verification_log["whys"] = []

    try:
        while not checked:
            logging.info("Beginning SerpAPI Searches.")
            search_results = await SearchAgent().run(
                request.subject, request.context, request.language
            )

            logging.info("Beginning Scraping and Preprocessing.")
            scraped_data = await ScraperAgent().run(
                search_results,
                request.subject + request.context
            )

            logging.debug(f"scraped_data: {scraped_data}")
            if not scraped_data:
                logging.warning("No data scraped from any site.")
                return AnalysisResponse(
                    trust_score=0.0,
                    details="Nessun dato recuperato dalle fonti."
                )

            logging.info("Beginning Validation.")
            checked_data = await VerifierAgent().run(
                scraped_data, request.language
            )

            logging.debug(f"checked_data: {checked_data}")
            if not checked_data or not checked_data.get("data"):
                logging.warning("Validation returned no data.")
                return AnalysisResponse(
                    trust_score=0.0,
                    details="Nessun dato valido dopo la validazione."
                )

            if checked_data["verified"] == "OK":
                checked = True
                verification_log["searches"].append(checked_data["data"])
            else:
                verification_log["searches"].append(checked_data["data"])
                verification_log["whys"].append(
                    checked_data["error_details"]["whys"]
                )
                if counter > __N_VALIDATION_RETRIES__:
                    checked = None
                    break
                else:
                    counter += 1

        if not checked:
            logging.warning("Validation failed or exceeded timeout.")
            return AnalysisResponse(
                trust_score=0.0,
                details=("Validazione non disponibile o "
                         "nessun risultato prodotto."
                         )
            )

        logging.info("Beginning Scoring.")
        score, details = await ScorerAgent().run(
            verification_log, request.language
        )

        if not details or not score:
            logging.warning("Scoring failed or returned no details.")
            return AnalysisResponse(
                trust_score=0.0,
                details="Scoring non disponibile o nessun dettaglio prodotto."
            )

        logging.info("Analysis complete.")
        return AnalysisResponse(trust_score=score, details=details)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", dependencies=[Security(azure_scheme)])
def health():
    """
    Health check endpoint.
    Returns API status and version.
    """
    return {"status": "ok", "version": __VERSION__}


@app.get("/")
def main_page():
    """
    Redirects root endpoint to health check.
    """
    return RedirectResponse(url="/health", status_code=301)
