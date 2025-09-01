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
            temperature=0.2
        )

    async def run(self, verified_data_log):

        prompt = """
            Usa i risultati (searches) forniti in formato JSON per assegnare
            uno score di fiducia (0-100), spiegandone le motivazioni.

            Le motivazioni devono indicare un primo paragrafo esplicativo
            sul soggetto della richiesta, per poi indicare i
            perchè è stato attribuito il dato score
            in maniera chiara ed esplicita.

            Esempio di formattazione JSON dei risultati:
            {{
            "searches": [
                "testo ricerca 1",
                "testo ricerca 2"
            ]
            }}
.
            Esempio di output JSON valido:
            {{"score": 85, "details": "Motivazione qui"}}

            Searches:
            {verified_data_log}
            """.format(verified_data_log=verified_data_log["searches"])

        result = self.llm.invoke(prompt)
        content = getattr(result, 'content', str(result))

        # BUG: known parser error. Implementing serialization fallback chain
        try:
            # 1: direct parse
            parsed = json.loads(content)
            return parsed['score'], parsed['details']
        except Exception:
            try:
                # 2: regex
                match = re.search(r'\{(?:[^{}]|\n|\r)*\}', content)
                if match:
                    json_str = match.group(0)
                    json_str = re.sub(r',\s*\}$', '}', json_str)
                    parsed = json.loads(json_str)
                    return (
                        parsed.get('score', None),
                        parsed.get('details', None)
                    )
                else:
                    return None, None

            except Exception:
                # 3: multiline regex
                score_match = re.search(
                    r'"score"\s*:\s*([0-9]+\.?[0-9]*)',
                    content
                )
                details_match = re.search(
                    r'"details"\s*:\s*"([\s\S]*?)"\s*[\}\n]',
                    content
                )
                score = float(score_match.group(1)) if score_match else None
                details = (
                    details_match.group(1).strip() if details_match else None
                )

                return score, details
