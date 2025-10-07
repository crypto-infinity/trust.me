
"""
Search Agents: enhances and gets search results from user query.
"""

import logging
from langchain_setup import llm

from langchain_setup import search_tool
from .prompt_templates import QUERY_DEFINER_PROMPT


class SearchAgent:
    def __init__(self):
        self.search_tool = search_tool
        self.llm = llm

    def define_queries(self, name, context, language="en-US") -> list[str]:

        prompt_template = QUERY_DEFINER_PROMPT
        response = self.llm.invoke(
            prompt_template.format(
                name=name,
                context=context,
                language=language
            )
        )
        # Expecting a JSON list as output
        import json
        response_content = getattr(
            response, 'content', str(response)
        ).strip()
        try:
            queries = json.loads(response_content)
            if isinstance(queries, list):
                return queries
            else:
                return [str(queries)]
        except Exception as e:
            print(f"Errore parsing JSON define_queries: {e}")
            return []

    async def run(
        self, subject: str, context: str, language: str
    ) -> list[str]:

        links = []
        queries = self.define_queries(subject, context, language)
        logging.debug(f"define_queries: queries generate: {queries}")
        for query in queries:
            logging.info(f"Search query: {query}")
            search_result = self.search_tool.run(query)
            logging.debug(f"search_tool.run({query}) result: {search_result}")

            query_links = [
                item["link"]
                for item in search_result.get("organic_results", [])
                if "link" in item
            ]
            logging.debug(f"query_links for query '{query}': {query_links}")
            if query_links:
                links.append(query_links)

        return links
