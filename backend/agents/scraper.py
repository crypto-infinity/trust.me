import re
import logging
import aiohttp
import asyncio
from bs4 import BeautifulSoup

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from langchain_setup import embeddings
from config import __TOPK_RESULTS__, __API_TIMEOUT__


class ScraperAgent:
    def __init__(self) -> None:
        """
        Initializes the ScraperAgent with embeddings for vector search.
        """
        self.embeddings = embeddings

    def is_valid_url(self, url):
        """
        Checks if the provided URL is valid.
        Args:
            url (str): URL string to validate.
        Returns:
            bool: True if valid, False otherwise.
        """
        return re.match(
            (
                r"^https?://[\w\-\.]+(:\d+)?"
                r"(/[\w\-\.~:/?#\[\]@!$&'\"()*+,;=%]*)?$"
            ),
            url,
            re.IGNORECASE,
        )

    async def fetch_site(self, url, headers, timeout=__API_TIMEOUT__):
        """
        Asynchronously fetches the HTML content of a web page.
        Args:
            url (str): The URL to fetch.
            headers (dict): HTTP headers to use.
            timeout (int | None): Timeout in seconds.
            If None, uses __API_TIMEOUT__ from config.
        Returns:
            str | None: Extracted text or None if failed.
        """
        if timeout is None:
            timeout = __API_TIMEOUT__
        try:
            async with aiohttp.ClientSession() as session:
                logging.debug("ClientSession spawned.")
                async with session.get(
                    url, headers=headers, timeout=timeout
                ) as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    for script in soup(["script", "style"]):
                        script.decompose()
                    return soup.get_text(separator=" ", strip=True)
        except Exception as e:
            logging.warning(f"Skipping site: {e}")
            return None

    def clean_text_gen(self, text):
        """
        Generator that cleans and segments extracted text from scraping.
        Args:
            text (str): Raw text extracted from a web page.
        Yields:
            str: Cleaned sentence longer than 15 and shorter than 1024 chars.
        """
        text = re.sub(r"\[\w+\]", "", text)
        text = re.sub(r"([^\w\s]{2,}|_{2,}|-{2,})", " ", text)
        text = re.sub(r"\s+", " ", text)
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for s in sentences:
            cleaned = "".join(
                c for c in s if 32 <= ord(c) <= 126 or c in "\n\r\t"
            ).strip()
            if 15 < len(cleaned) < 1024 and not cleaned.isdigit():
                yield cleaned

    async def limited_fetch(self,
                            url,
                            headers,
                            semaphore,
                            timeout=__API_TIMEOUT__):
        """
        Wrapper for fetch_site with semaphore and timeout.
        Args:
            url (str): The URL to fetch.
            headers (dict): HTTP headers to use.
            semaphore (asyncio.Semaphore): Semaphore for limiting concurrency.
            timeout (int | None): Timeout in seconds.
            If None, uses __API_TIMEOUT__.
        Returns:
            str | None: Extracted text or None if failed.
        """
        async with semaphore:
            logging.debug("Process spawned.")
            return await self.fetch_site(url, headers, timeout=timeout)

    async def run(
        self,
        search_results: list[str],
        user_query: str,
        top_k: int = __TOPK_RESULTS__,
        n_jobs: int = 5
    ) -> list[str]:
        """
        Extracts the most relevant text chunks for the user's query from web
        pages using LangChain and AzureOpenAIEmbeddings.
        Optimized for low RAM usage and parallel requests.
        Args:
            search_results (list[str]): List of URLs to extract text from.
            user_query (str): The user's query string.
            top_k (int): Number of most similar chunks to return.
            n_jobs (int): Number of maximum processes to spawn.
        Returns:
            list[str]: List of relevant text chunks.
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.google.com/",
        }

        sem = asyncio.Semaphore(n_jobs)

        links = [
            url for url in search_results if self.is_valid_url(url)
            ][:top_k]
        tasks = [
            self.limited_fetch(url, headers, sem, timeout=__API_TIMEOUT__)
            for url in links
        ]
        texts = await asyncio.gather(*tasks)

        docs = []
        for text in texts:
            if text:
                for chunk in self.clean_text_gen(text):
                    docs.append(Document(page_content=chunk))

        if not docs:
            return []

        vectorstore = FAISS.from_documents(docs, self.embeddings)
        results = vectorstore.similarity_search(user_query, k=top_k)
        relevant_chunks = [doc.page_content for doc in results]
        return relevant_chunks
