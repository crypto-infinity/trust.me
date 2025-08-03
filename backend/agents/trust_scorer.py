import os
import json
import re
from langchain_openai import AzureChatOpenAI


class TrustScorerAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
            temperature=0.1
        )

    async def run(self, verified_data):

        prompt = (
            "Sulla base di queste informazioni verificate, assegna uno score di fiducia (0-100) e spiega le motivazioni.\n"
            f"{verified_data['data']}\n"
            "Rispondi SOLO con un oggetto JSON valido, senza testo extra, senza virgola finale dopo l'ultimo campo.\n"
            "Esempio: {\"score\": 85, \"details\": \"Motivazione qui\"}"
        )
        result = self.llm.invoke(prompt)
        content = getattr(result, 'content', str(result))
        # Prova parsing diretto
        try:
            parsed = json.loads(content)
            return parsed['score'], parsed['details']
        except Exception as e1:
            # Prova ad estrarre il primo oggetto JSON valido dalla risposta (multilinea, solo tra graffe)
            try:
                match = re.search(r'\{(?:[^{}]|\n|\r)*\}', content)
                if match:
                    json_str = match.group(0)
                    # Rimuovi eventuale virgola finale prima della chiusura
                    json_str = re.sub(r',\s*\}$', '}', json_str)
                    parsed = json.loads(json_str)
                    return parsed.get('score', 50.0), parsed.get('details', {'error': 'Dettagli non trovati'})
            except Exception:
                pass
            # Fallback: estrai score e details con regex multilinea e usali SEMPRE per il report
            score_match = re.search(r'"score"\s*:\s*([0-9]+\.?[0-9]*)', content)
            details_match = re.search(r'"details"\s*:\s*"([\s\S]*?)"\s*[\}\n]', content)
            score = float(score_match.group(1)) if score_match else 50.0
            details = details_match.group(1).strip() if details_match else 'Parsing LLM fallito'

            return score, details
