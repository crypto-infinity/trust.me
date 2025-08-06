from bs4 import BeautifulSoup
import requests
import json
import re

class ScraperAgent:
            
    def is_valid_url(self, url):
        # Regex semplificata e corretta per http/https
        return re.match(r'^https?://[\w\-\.]+(:\d+)?(/[\w\-\.~:/?#\[\]@!$&\'"()*+,;=%]*)?$', url, re.IGNORECASE)
    
    async def run(self, search_results: list[str]) -> list[str]:

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

        print(links)

        for url in links[:10]:
            try:
                resp = requests.get(url, timeout=10, headers=headers)
                soup = BeautifulSoup(resp.text, 'html.parser')

                # Estrai solo testo significativo (rimuovi script/style)
                for script in soup(["script", "style"]):
                    script.decompose()

                text = soup.get_text(separator=' ', strip=True)
                phrases = [f.strip() for f in text.split('. ')]

                texts.extend(phrases)
            except Exception as e:
                print(e)

        # Restituisci tutte le frasi rilevanti estratte
        return texts
