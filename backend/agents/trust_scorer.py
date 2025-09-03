
import os
import json
import re
from pydantic import SecretStr
from langchain_openai import AzureChatOpenAI
from langsmith import Client


class TrustScorerAgent:
    def __init__(self):
        """
        Initializes the TrustScorerAgent with AzureChatOpenAI.
        Requires the following environment variables:
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_ENDPOINT
        - AZURE_OPENAI_DEPLOYMENT
        - AZURE_OPENAI_MODEL (optional, defaults to 'gpt-35-turbo')
        """
        self.llm = AzureChatOpenAI(
            api_key=SecretStr(os.getenv("AZURE_OPENAI_API_KEY") or ""),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
            temperature=0.2
        )

    async def run(self, verified_data_log):
        """
        Computes a trust score (0-100) and explanatory details using the
        provided search results log.
        Requires Azure OpenAI environment variables as set in __init__.
        Args:
            verified_data_log: Dictionary containing 'searches' key with list
            of search result texts.
        Returns:
            Tuple (score: float, details: str) with the trust score and
            explanation.
        """

        client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        prompt_template = client.pull_prompt(
            "scorer"
        )
        result = self.llm.invoke(
            prompt_template.format(
                **{"verified_data_log": verified_data_log["searches"]}
            )
        )
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
