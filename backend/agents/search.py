from langchain.agents import Tool
from langchain_community.utilities.serpapi import SerpAPIWrapper

class SearchAgent:
    def __init__(self):
        self.search_tool = Tool(
            name="search",
            func=SerpAPIWrapper().run,
            description="Cerca informazioni pubbliche su persone o aziende tramite SerpAPI."
        )

    async def run(self, subject: str, context: str, query_suffix: str):
        query = f"{subject} {context} {query_suffix}"
        return self.search_tool.run(query)
