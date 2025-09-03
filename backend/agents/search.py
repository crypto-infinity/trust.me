
import os
from pydantic import SecretStr
from langsmith import Client
from langchain.agents import Tool
from langchain_community.utilities.serpapi import SerpAPIWrapper
from langchain_openai import AzureChatOpenAI


class SearchAgent:
    def __init__(self):

        def search_func(query):
            result = SerpAPIWrapper().results(query)
            return result

        self.search_tool = Tool(
            name="search",
            func=search_func,
            description=(
                "Cerca informazioni pubbliche su persone o aziende"
                "tramite SerpAPI."
            ),
        )

        self.llm = AzureChatOpenAI(
            api_key=SecretStr(os.getenv("AZURE_OPENAI_API_KEY") or ""),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1"),
            temperature=0.2
        )

    def define_query(self, name, context, suggestion=""):
        """
        Generates an enhanced search query for assessing the trustworthiness
        of a person or company.
        """
        client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        prompt_template = client.pull_prompt("query_rewriter")

        response = self.llm.invoke(
            prompt_template.format(name=name,
                                   context=context,
                                   suggestion=suggestion)
        )

        return getattr(response, 'content', str(response)).strip()

    async def run(
        self, subject: str, context: str, query_suffix: str
    ) -> list[str]:
        """
        Performs a web search based on subject, context, and query.
        Does not require environment variables in placeholder implementation.
        Args:
            subject: The person or company name to search for.
            context: The search context string.
            query_suffix: Additional query string for refining search.
        Returns:
            List of URLs as search results.
        """
        query = self.define_query(subject, context, query_suffix)
        result = self.search_tool.run(query)

        links = [
            item["link"]
            for item in result.get("organic_results", [])
            if "link" in item
        ]
        return links
