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
        
    def clean_text(self, chunks):
        # Se è una lista, unisci tutto in un testo unico
        if isinstance(chunks, list):
            text = ' '.join(chunks)
        else:
            text = str(chunks)
        # Rimuovi riferimenti tipo [1], [a], ecc.
        text = re.sub(r'\[\w+\]', '', text)
        # Rimuovi sequenze di simboli o caratteri ripetuti
        text = re.sub(r'([^\w\s]{2,}|_{2,}|-{2,})', ' ', text)
        # Rimuovi eccessi di spazi
        text = re.sub(r'\s+', ' ', text)
        # Suddividi in frasi
        sentences = re.split(r'(?<=[.!?])\s+', text)
        # Tieni solo caratteri stampabili e ASCII e filtra frasi troppo corte (>15 caratteri)
        cleaned = [''.join(c for c in s if 32 <= ord(c) <= 126 or c in '\n\r\t').strip() for s in sentences]
        cleaned = [s for s in cleaned if len(s) > 15 and not s.isdigit()]
        return cleaned
            
    def is_valid_url(self, url):
        # Regex semplificata e corretta per http/https
        return re.match(r'^https?://[\w\-\.]+(:\d+)?(/[\w\-\.~:/?#\[\]@!$&\'"()*+,;=%]*)?$', url, re.IGNORECASE)
    
    async def run(
        self,
        search_results: list[str],
        user_query: str,
        top_k: int = 10
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
                texts.append(text)
            except Exception as e:
                print(e)

        if not texts: return []


        cleaned_chunks = self.clean_text(texts) or []

        # Calcola embedding per query e chunk
        query_emb = np.array(self.embeddings.embed_query(user_query))
        chunk_embs = np.array(self.embeddings.embed_documents(cleaned_chunks))

        # Calcola similarità coseno
        similarities = np.dot(chunk_embs, query_emb) / (np.linalg.norm(chunk_embs, axis=1) * np.linalg.norm(query_emb) + 1e-8)
        top_indices = similarities.argsort()[::-1][:top_k]

        relevant_chunks = [cleaned_chunks[i] for i in top_indices]

        return relevant_chunks
