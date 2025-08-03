from bs4 import BeautifulSoup
import requests
import json

class ScraperAgent:
    async def run(self, search_results: dict | str) -> list[dict]:
        # Gestione robusta del tipo di input
        if isinstance(search_results, str):
            try:
                search_results = json.loads(search_results)
            except Exception:
                return []
        if not isinstance(search_results, dict):
            return []
        scraped = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        print(search_results)
        for url in search_results.get('links', []):
            try:
                resp = requests.get(url, timeout=5, headers=headers)
                soup = BeautifulSoup(resp.text, 'html.parser')
                scraped.append({
                    'url': url,
                    'title': soup.title.string if soup.title else '',
                    'text': soup.get_text()
                })
            except Exception as e:
                print(e)
        return scraped
