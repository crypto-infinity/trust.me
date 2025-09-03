
import re
import logging
import requests
from bs4 import BeautifulSoup

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from langchain_setup import embeddings
from config import __TOPK_RESULTS__


class ScraperAgent:
    def __init__(self) -> None:
        self.embeddings = embeddings

    def clean_text(self, chunks):
        """
        Cleans and segments the extracted text from scraping.
        Args:
            chunks: List or string of raw text extracted from web pages.
        Returns:
            List of cleaned sentences longer than 15 characters.
        """
        if isinstance(chunks, list):
            text = ' '.join(chunks)
        else:
            text = str(chunks)
        text = re.sub(r'\[\w+\]', '', text)
        text = re.sub(r'([^\w\s]{2,}|_{2,}|-{2,})', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        cleaned = [
            ''.join(
                c for c in s if 32 <= ord(c) <= 126 or c in '\n\r\t'
            ).strip()
            for s in sentences
        ]
        cleaned = [s for s in cleaned if len(s) > 15 and not s.isdigit()]
        return cleaned

    def is_valid_url(self, url):
        """
        Checks if the provided URL is valid.
        Args:
            url: URL string to validate.
        Returns:
            True if valid, False otherwise.
        """
        return re.match(
            r'^https?://[\w\-\.]+(:\d+)?'
            r'(/[\w\-\.~:/?#\[\]@!$&\'"()*+,;=%]*)?$',
            url,
            re.IGNORECASE
        )

    async def run(
        self,
        search_results: list[str],
        user_query: str,
        top_k: int = __TOPK_RESULTS__
    ) -> list[str]:
        """
        Extracts the most relevant text chunks for the user's query from web
        pages using LangChain and AzureOpenAIEmbeddings.
        Args:
            search_results: List of URLs to extract text from.
            user_query: The user's query string.
            top_k: Number of most similar chunks to return.
        Returns:
            List of relevant text chunks.
        """
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/115.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/webp,*/*;q=0.8'
            ),
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/'
        }

        texts = []

        links = [
            url for url in search_results if self.is_valid_url(url)
        ][:top_k]

        for url in links:
            try:
                resp = requests.get(url, timeout=10, headers=headers)
                soup = BeautifulSoup(resp.text, 'html.parser')
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator=' ', strip=True)
                texts.append(text)
            except Exception as e:
                logging.warning(f"Skipping site: {e}")
                continue

        if not texts:
            return []

        cleaned_chunks = self.clean_text(texts)
        docs = [Document(page_content=chunk) for chunk in cleaned_chunks]
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        results = vectorstore.similarity_search(user_query, k=top_k)
        relevant_chunks = [doc.page_content for doc in results]

        return relevant_chunks
