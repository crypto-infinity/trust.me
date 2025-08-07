import os
import json
import re
from langchain_openai import AzureChatOpenAI


class TrustScorerAgent:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  # type: ignore
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
            temperature=0.1
        )

    async def run(self, verified_data_log):

        prompt = """
            Usa le ricerche (searches) e i commenti del verifier agent (whys) in formato JSON 
            per assegnare uno score di fiducia (0-100) e spiega le motivazioni.

            Esempio di formattazione JSON di input:
            {{
            "searches": [
                "testo ricerca 1",
                "testo ricerca 2"
            ],
            "whys": [
                "commento sulla ricerca 1",
                "commento sulla ricerca 2"
            ]
            }}

            Input:
            {verified_data_log}
.
            Esempio di output JSON valido: {{"score": 85, "details": "Motivazione qui"}}
            """.format(verified_data_log = verified_data_log)
        
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
