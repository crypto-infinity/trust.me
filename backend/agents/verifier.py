
"""
Verifier agent: validates scraper text chunks and provides feedback
"""
import json

from langchain_setup import llm
from .prompt_templates import VERIFIER_PROMPT


class VerifierAgent():

    def __init__(self):
        self.llm = llm

    async def run(self, text_chunks, language):
        """
        Verifies the consistency and reliability of the provided information
          chunks using AzureChatOpenAI.
        Requires Azure OpenAI environment variables as set in __init__.
        Args:
            text_chunks: List of strings, each representing extracted
              information from different sources.
            language: the output language
        Returns:
            Dictionary with keys:
                - 'verified': 'OK' if all information is consistent, otherwise
                  a JSON string with reasons and suggested retry query.
                - 'data': the input texts.
                - 'error_details': parsed error details or 'NO'.
        """

        if not isinstance(text_chunks, list):
            text_chunks = [str(text_chunks)]
        texts = [str(x) for x in text_chunks if x]

        prompt_template = VERIFIER_PROMPT

        result = self.llm.invoke(
            prompt_template.format(
                text_chunks=texts,
                language=language)
        )
        content = getattr(result, 'content', str(result))

        if content != "OK":
            try:
                error_details = json.loads(content)
            except Exception:
                error_details = content
        else:
            error_details = "NO"

        return {
            "verified": content,
            "data": texts,
            "error_details": error_details,
        }
