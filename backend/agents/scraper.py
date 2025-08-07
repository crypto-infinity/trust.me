from langchain_openai import AzureOpenAIEmbeddings
import numpy as np
from bs4 import BeautifulSoup
import requests
import os
import re

class ScraperAgent:

    def __init__(self) -> None:
        # Inizializza embeddings Azure OpenAI in modo uniforme con variabili di ambiente
        
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
        )
        
    def clean_text(self, s):
        # Tieni solo caratteri stampabili e ASCII
        return ''.join(c for c in s if 32 <= ord(c) <= 126 or c in '\n\r\t').strip()
            
    def is_valid_url(self, url):
        # Regex semplificata e corretta per http/https
        return re.match(r'^https?://[\w\-\.]+(:\d+)?(/[\w\-\.~:/?#\[\]@!$&\'"()*+,;=%]*)?$', url, re.IGNORECASE)
    
    async def run(
        self,
        search_results: list[str],
        user_query: str,
        top_k: int = 5
    ) -> list[str]:
        """
        Estrae i chunk di testo più rilevanti rispetto alla query dell'utente dalle pagine web usando LangChain e AzureOAIEmbeddings.
        Tutti i parametri di configurazione Azure OpenAI (deployment, endpoint, chiave, versione) devono essere forniti tramite variabili d'ambiente:
        - AZURE_OPENAI_DEPLOYMENT_NAME
        - AZURE_OPENAI_ENDPOINT
        - OPENAI_API_KEY
        - OPENAI_API_VERSION
        Args:
            search_results: lista di URL da cui estrarre il testo
            user_query: la query dell'utente
            top_k: numero di chunk più simili da restituire
        Returns:
            Lista di chunk di testo rilevanti
        """
        texts = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/'
        }

        # Check for valid links
        links = [url for url in search_results if self.is_valid_url(url)]

        for url in links:
            try:
                resp = requests.get(url, timeout=10, headers=headers)
                soup = BeautifulSoup(resp.text, 'html.parser')

                # Estrai solo testo significativo (rimuovi script/style)
                for script in soup(["script", "style"]):
                    script.decompose()

                text = soup.get_text(separator=' ', strip=True)

                # Suddividi in frasi/chunk e rimuovi caratteri non ASCII o non leggibili
                phrases = [self.clean_text(f) for f in text.split('. ') if len(self.clean_text(f)) > 30]

                texts.extend(phrases)
            except Exception as e:
                print(e)

        if not texts:
            return []

        # Calcola embedding per query e chunk
        query_emb = np.array(self.embeddings.embed_query(user_query))
        chunk_embs = np.array(self.embeddings.embed_documents(texts))

        # Calcola similarità coseno
        similarities = np.dot(chunk_embs, query_emb) / (np.linalg.norm(chunk_embs, axis=1) * np.linalg.norm(query_emb) + 1e-8)
        top_indices = similarities.argsort()[::-1][:top_k]

        relevant_chunks = [texts[i] for i in top_indices]
        return relevant_chunks
