import os
from langchain_openai import AzureChatOpenAI

class VerifierAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
            temperature=0.2
        )

    async def run(self, scraped_data):
        texts = [item['text'] for item in scraped_data]
        prompt = f"""Verifica la coerenza e l'attendibilità delle seguenti informazioni:\n{texts}\nRispondi con un elenco di anomalie o 'OK' se tutto è coerente."""
        result = self.llm.invoke(prompt)
        return {'verified': result, 'data': scraped_data}
