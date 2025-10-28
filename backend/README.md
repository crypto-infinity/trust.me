# Trust.me Backend

FastAPI + LangChain backend for agentic orchestration of trust evaluation.

## Agent Structure
- **SearchAgent**: Searches public profiles (Serper)
- **ScraperAgent**: Extracts data from links
- **VerifierAgent**: Checks consistency and reliability (LLM)
- **TrustScorerAgent**: Calculates trust score (LLM)
- **HumanCheckAgent**: Optional human validation - not implemented
- **ReportAgent**: Generates markdown reports

## Local Startup
1. Copy `.env.example` to `.env` and enter your API keys
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Start the server:
   ```sh
   uvicorn main:app --reload
   ```

## Notes
- Requires Azure OpenAI keys (with a configured LLM and embeddings model) and Serper

