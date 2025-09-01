import os
import json
from langchain_openai import AzureChatOpenAI


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
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  # type: ignore
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
        if not isinstance(text_chunks, list):
            text_chunks = [str(text_chunks)]
        texts = [str(x) for x in text_chunks if x]

        prompt = """Verifica la coerenza e l'attendibilità delle seguenti
                    informazioni
                    (ogni elemento è un estratto da fonti diverse):
                     {text_chunks}

                     Rispondi solo 'OK' se tutto è coerente, oppure rispondi
                     con un JSON formato da:
                     - whys: motivazioni sul perchè non sono coerenti le
                        informazioni, rappresentate da una lista di frasi
                        con almeno una frase all'interno.
                     - suggested_retry: una query generica per motore di
                        ricerca per variabilizzare la ricerca di nuove
                        informazioni sulla persona o sull'azienda menzionate.

                     Non includere nella suggested retry il soggetto,
                     il tipo di soggetto e il contesto fornito
                     in precedenza dall'utente.

                     Esempio di formattazione JSON:
                     {{
                        "whys": [
                            "motivazione 1",
                            "motivazione 2"
                        ],
                        "suggested_retry": "social profile linkedin crunchbase"
                     }}
                """.format(
            text_chunks=texts
        )

        result = json.loads(
            self.llm.invoke(prompt).model_dump_json()
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
