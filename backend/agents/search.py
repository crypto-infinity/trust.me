from langchain.agents import Tool
from langchain_community.utilities.serpapi import SerpAPIWrapper

class SearchAgent:
    def __init__(self):
        self.search_tool = Tool(
            name="search",
            func=SerpAPIWrapper().run,
            description="Cerca informazioni pubbliche su persone o aziende tramite SerpAPI."
        )

    async def run(self, subject: str, context: str, query_suffix: str) -> list[str]:
        query = f"{subject} {context} {query_suffix}"
        result = self.search_tool.run(query)

        print(type(result))

        # Se il risultato è una stringa che rappresenta una lista
        if isinstance(result, str):
            s = result.strip()
            if s.startswith("[") and s.endswith("]"):
                # Rimuovi le parentesi quadre e dividi per ", '"
                s = s[1:-1]
                # Gestione sia apici singoli che doppi
                items = []
                temp = ""
                in_string = False
                quote = None
                for c in s:
                    if c in "'\"" and not in_string:
                        in_string = True
                        quote = c
                        temp = ""
                    elif c == quote and in_string:
                        in_string = False
                        items.append(temp)
                        quote = None
                    elif in_string:
                        temp += c
                return [i for i in items if i.strip()]
            else:
                return [result]
        elif isinstance(result, list):
            return [str(x) for x in result]
        else:
            return [str(result)]
