
import json
import re
from langchain_setup import llm
from .prompt_templates import SCORER_PROMPT


class ScorerAgent:
    def __init__(self):
        self.llm = llm

    async def run(self, verified_data_log, language):
        """
        Computes a trust score (0-100) and explanatory details using the
        provided search results log.
        Requires Azure OpenAI environment variables as set in __init__.
        Args:
            verified_data_log: Dictionary containing 'searches' key with list
            of search result texts.
            language: the output language.
        Returns:
            Tuple (score: float, details: str) with the trust score and
            explanation.
        """

        prompt_template = SCORER_PROMPT
        result = self.llm.invoke(
            prompt_template.format(
                verified_data_log=verified_data_log["searches"],
                language=language
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
