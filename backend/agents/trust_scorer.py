import os
from langchain_openai import AzureChatOpenAI

class TrustScorerAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
            temperature=0.1
        )

    async def run(self, verified_data):
        prompt = f"""Sulla base di queste informazioni verificate, assegna uno score di fiducia (0-100) e spiega le motivazioni:\n{verified_data['data']}\nOutput JSON: {{'score': <float>, 'details': <spiegazione>}}"""
        result = self.llm.invoke(prompt)
        import json
        try:
            parsed = json.loads(result.replace("'", '"'))
            return parsed['score'], parsed['details']
        except Exception:
            return 50.0, {'error': 'Parsing LLM fallito'}
