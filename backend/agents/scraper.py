from bs4 import BeautifulSoup
import requests

class ScraperAgent:
    async def run(self, search_results):
        # Esempio: estrai link e fai scraping base
        scraped = []
        for url in search_results.get('links', []):
            try:
                resp = requests.get(url, timeout=5)
                soup = BeautifulSoup(resp.text, 'html.parser')
                scraped.append({
                    'url': url,
                    'title': soup.title.string if soup.title else '',
                    'text': soup.get_text()[:1000]  # Limita testo
                })
            except Exception:
                continue
        return scraped
