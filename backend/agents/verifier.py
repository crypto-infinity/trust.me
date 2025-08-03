import os
from langchain_openai import AzureChatOpenAI

class VerifierAgent:
    @staticmethod
    def extract_text_chunks(search_results):
        """Estrae una lista di chunk testuali da search_results, gestendo dict, list, str."""
        text_chunks = []
        if isinstance(search_results, dict):
            links = search_results.get('links')
            if isinstance(links, list):
                text_chunks = [str(x) for x in links]
            elif isinstance(links, str):
                text_chunks = [links]
        elif isinstance(search_results, list):
            text_chunks = [str(x) for x in search_results]
        elif isinstance(search_results, str):
            text_chunks = [search_results]
        return text_chunks
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
            temperature=0.2
        )

    @staticmethod
    def normalize_search_results(search_results):
        """Normalizza i risultati della ricerca in un dict con chiave 'links'."""
        if isinstance(search_results, dict) and 'links' in search_results:
            return search_results
        elif isinstance(search_results, list):
            if all(isinstance(x, str) for x in search_results):
                return {'links': search_results}
            else:
                return {'links': []}
        elif isinstance(search_results, str):
            return {'links': [search_results]}
        else:
            return {'links': []}

    @staticmethod
    def validate_scraped_data(scraped_data):
        """Restituisce una lista di dict con chiave 'text', oppure lista vuota se non valida."""
        if not isinstance(scraped_data, list):
            return []
        valid = [item for item in scraped_data if isinstance(item, dict) and 'text' in item]
        return valid

    async def run(self, text_chunks):
        # text_chunks è una lista di stringhe
        if not isinstance(text_chunks, list):
            text_chunks = [str(text_chunks)]
        texts = [str(x) for x in text_chunks if x]
        prompt = f"""Verifica la coerenza e l'attendibilità delle seguenti informazioni (ogni elemento è un estratto da fonti diverse):\n{texts}\nRispondi con un elenco di anomalie o 'OK' se tutto è coerente."""
        result = self.llm.invoke(prompt)
        return {'verified': result, 'data': texts}
