
"""
Search Agents: enhances and gets search results from user query.
"""
from langchain_setup import llm
from langchain_setup import langsmith_client
from langchain_setup import search_tool


class SearchAgent:
    def __init__(self):
        self.langsmith_client = langsmith_client
        self.search_tool = search_tool
        self.llm = llm

    def define_queries(self, name, context, language="en-US") -> list[str]:
        """
        Generates an enhanced search query for assessing the trustworthiness
        of a person or company.
        """

        results = []
        prompt_template = langsmith_client.pull_prompt("query_definer")

        response = self.llm.invoke(
            prompt_template.format(name=name,
                                   context=context,
                                   language=language)
        )

        for item in getattr(response, 'content', str(response)).strip():
            results.append(item)

        return results or []

    async def run(
        self, subject: str, context: str, language: str
    ) -> list[str]:
        """
        Performs a web search based on subject, context, and query.
        Does not require environment variables in placeholder implementation.
        Args:
            subject: The person or company name to search for.
            context: The search context string.
            query_suffix: Additional query string for refining search.
            language: the output language.
        Returns:
            List of URLs as search results.
        """

        results = []
        links = []
        queries = self.define_queries(subject, context, language)

        for query in queries:

            search_result = self.search_tool.run(query)
            results.append(self.search_tool.run(query))

            query_links = [
                item["link"]
                for item in search_result.get("organic_results", [])
                if "link" in item
            ]

            links.append(query_links)

        return links
