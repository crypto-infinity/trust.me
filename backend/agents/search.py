from langchain.agents import Tool
from langchain_community.utilities.serpapi import SerpAPIWrapper

class SearchAgent:
    def __init__(self):
        self.search_tool = Tool(
            name="search",
            func=SerpAPIWrapper().run,
            description="Cerca informazioni pubbliche su persone o aziende tramite SerpAPI."
        )

    async def run(self, subject: str, subject_type: str, context: str, query_suffix: str):
        query = f"{subject} {subject_type} {context} {query_suffix}"
        results = self.search_tool.run(query)

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

        # Suddividi i testi in frasi complete usando il punto
        phrases = []
        for t in texts:
            phrases.extend([f.strip() for f in t.split('. ') if len(f.strip()) > 20])

        # Restituisci solo frasi non vuote
        return phrases if phrases else texts
