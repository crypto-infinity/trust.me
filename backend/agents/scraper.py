from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

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
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/'
        }

        texts = []

        # Check for valid links
        links = [url for url in search_results if self.is_valid_url(url)]

        for url in links:
            try:
                resp = requests.get(url, timeout=10, headers=headers)
                soup = BeautifulSoup(resp.text, 'html.parser')

                for script in soup(["script", "style"]): script.decompose()

                text = soup.get_text(separator=' ', strip=True)
                texts.append(text)
            except ConnectionError as e:
                print(f"INFO - Skipping: {e}")

        if not texts: return []

        #Preprocessing
        cleaned_chunks = self.clean_text(texts)

        #Vector Store
        docs = [Document(page_content=chunk) for chunk in cleaned_chunks]
        vectorstore = FAISS.from_documents(docs, self.embeddings)

        #Similarity search
        results = vectorstore.similarity_search(user_query, k=top_k)
        relevant_chunks = [doc.page_content for doc in results]

        return relevant_chunks
