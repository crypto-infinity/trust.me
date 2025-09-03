import os
import json
from langchain_openai import AzureChatOpenAI
from langsmith import Client
from pydantic import SecretStr


class VerifierAgent:

    def __init__(self):
        """
        Initializes the VerifierAgent with AzureChatOpenAI.
        Requires the following environment variables:
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_DEPLOYMENT
        - AZURE_OPENAI_MODEL (optional, defaults to 'gpt-35-turbo')
        """
        self.llm = AzureChatOpenAI(
            api_key=SecretStr(os.getenv("AZURE_OPENAI_API_KEY") or ""),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
            temperature=0.2,
        )

    async def run(self, text_chunks):
        """
        Verifies the consistency and reliability of the provided information
          chunks using AzureChatOpenAI.
        Requires Azure OpenAI environment variables as set in __init__.
        Args:
            text_chunks: List of strings, each representing extracted
              information from different sources.
        Returns:
            Dictionary with keys:
                - 'verified': 'OK' if all information is consistent, otherwise
                  a JSON string with reasons and suggested retry query.
                - 'data': the input texts.
                - 'error_details': parsed error details or 'NO'.
        """

        client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        if not isinstance(text_chunks, list):
            text_chunks = [str(text_chunks)]
        texts = [str(x) for x in text_chunks if x]

        prompt_template = client.pull_prompt(
            "verifier"
        )

        result = json.loads(
            self.llm.invoke(
                prompt_template.format(text_chunks=texts)
            ).model_dump_json()
        )["content"]

        if result != "OK":
            error_details = json.loads(result)
        else:
            error_details = "NO"

        return {
            "verified": result,
            "data": texts,
            "error_details": error_details,
        }
