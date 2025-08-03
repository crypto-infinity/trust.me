from langchain.agents import Tool
from langchain_community.utilities.serpapi import SerpAPIWrapper
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class SearchAgent:
    def __init__(self):
        self.tool = Tool(
            name="search",
            func=SerpAPIWrapper().run,
            description="Cerca informazioni pubbliche su persone o aziende tramite SerpAPI."
        )
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
            model=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
            chunk_size=2048
        )

    async def run(self, subject: str, subject_type: str):
        query = f"{subject} {subject_type} social profile linkedin crunchbase"
        results = self.tool.run(query)
        # Estrai i testi dai risultati SerpAPI (assumendo formato stringa o lista di dict)
        texts = []
        if isinstance(results, str):
            texts.append(results)
        elif isinstance(results, list):
            for r in results:
                if isinstance(r, dict):
                    texts.append(r.get('snippet', '') or r.get('text', ''))
                elif isinstance(r, str):
                    texts.append(r)
        # Split in chunk
        all_chunks = []
        for t in texts:
            all_chunks.extend(self.text_splitter.split_text(t))
        # Restituisci tutti i chunk senza ranking
        return all_chunks if all_chunks else texts
