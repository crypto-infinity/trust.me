
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

    def define_query(self, name, context, suggestion="", language="en-US"):
        """
        Generates an enhanced search query for assessing the trustworthiness
        of a person or company.
        """
        prompt_template = langsmith_client.pull_prompt("query_rewriter")

        response = self.llm.invoke(
            prompt_template.format(name=name,
                                   context=context,
                                   suggestion=suggestion,
                                   language=language)
        )

        return getattr(response, 'content', str(response)).strip()

    async def run(
        self, subject: str, context: str, query_suffix: str, language: str
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
        query = self.define_query(subject, context, query_suffix, language)
        result = self.search_tool.run(query)

        links = [
            item["link"]
            for item in result.get("organic_results", [])
            if "link" in item
        ]
        return links
