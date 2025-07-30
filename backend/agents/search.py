from langchain.agents import Tool
from langchain_community.utilities.serpapi import SerpAPIWrapper

class SearchAgent:
    def __init__(self):
        self.tool = Tool(
            name="search",
            func=SerpAPIWrapper().run,
            description="Cerca informazioni pubbliche su persone o aziende tramite SerpAPI."
        )

    async def run(self, subject: str, subject_type: str):
        # Puoi arricchire la query in base al tipo
        query = f"{subject} {subject_type} social profile linkedin crunchbase"
        return self.tool.run(query)
