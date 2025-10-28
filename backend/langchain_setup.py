
"""
Langchain setup: creates instances of langchain tools/models.
"""
import os
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings

from langchain.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langsmith import Client

from config import __TOPK_RESULTS__

load_dotenv()


# Initializes an LLM istance
llm = AzureChatOpenAI(
    api_key=SecretStr(os.getenv("AZURE_OPENAI_API_KEY") or ""),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1"),
    temperature=0.2
)

# Initializes the embedding model instance
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.environ.get(
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    ),
    azure_endpoint=os.environ.get(
        "AZURE_OPENAI_ENDPOINT"
    )
)

# Initializes Langsmith Client
langsmith_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))


# Inizializza GoogleSerperAPIWrapper
google_search = GoogleSerperAPIWrapper(k=__TOPK_RESULTS__)


def search_func(query):
    result = google_search.results(query)
    return result


search_tool = Tool(
    name="search",
    func=search_func,
    description=(
        "Search public informations with GoogleSerperAPI."
    )
)
