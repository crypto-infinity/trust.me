
from langchain.agents import Tool
from langchain_community.utilities.serpapi import SerpAPIWrapper


class SearchAgent:
    def __init__(self):

        def search_func(query):
            result = SerpAPIWrapper().results(query)
            return result

        self.search_tool = Tool(
            name="search",
            func=search_func,
            description=(
                "Cerca informazioni pubbliche su persone o aziende "
                "tramite SerpAPI."
            ),
        )

    async def run(
        self, subject: str, context: str, query_suffix: str, params: dict = {}
    ) -> list[str]:
        query = f"{subject} {context} {query_suffix}"
        result = self.search_tool.run(query)

        # Estrai i link dai risultati organici
        links = [
            item["link"]
            for item in result.get("organic_results", [])
            if "link" in item
        ]
        return links
