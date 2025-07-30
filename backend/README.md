# Trust.me Backend

Backend FastAPI + LangChain per orchestrazione agentica della valutazione della fiducia.

## Struttura agenti
- **SearchAgent**: Ricerca profili pubblici (SerpAPI)
- **ScraperAgent**: Estrazione dati da link
- **VerifierAgent**: Verifica coerenza e attendibilità (LLM)
- **TrustScorerAgent**: Calcolo score di fiducia (LLM)
- **HumanCheckAgent**: Validazione umana opzionale
- **ReportAgent**: Generazione report markdown

## Avvio locale
1. Copia `.env.example` in `.env` e inserisci le chiavi API
2. Installa le dipendenze:
   ```sh
   pip install -r requirements.txt
   ```
3. Avvia il server:
   ```sh
   uvicorn main:app --reload
   ```

## Note
- Richiede chiavi OpenAI e SerpAPI
- Per scraping avanzato, aggiungi Scrapy o altri tool
- Per produzione, configura SQL Server e OAuth
