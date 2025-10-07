"""
Prompt templates for TrustME agents.
"""

from langchain.prompts import PromptTemplate

QUERY_DEFINER_PROMPT = PromptTemplate(
    input_variables=["name", "language", "context"],
    template=(
        "You are an OSINT research agent. "
        "You receive as input the name of a company or individual "
        "(e.g., 'OpenAI', 'Gabriele Scorpaniti') and some context. "
        "Your task is to generate a list of search queries, in the specified "
        "language and optimized for SerpApi, tailored to the type of the input"
        " provided.\n\n"
        "Generate one query string ready to be used with SerpApi. Queries "
        "should include Boolean operators, quotation marks for exact phrases,"
        "and specific "
        "keywords to increase precision. If the subject is a person, adapt the"
        " categories accordingly. Use the context only if relevant.\n\n"
        "Example output for 'OpenAI':\n"
        "- 'OpenAI company profile site:linkedin.com'\n"
        "- 'OpenAI recent news site:cnn.com OR site:bbc.com'\n"
        "- 'OpenAI controversy OR criticism OR lawsuit'\n"
        "- 'OpenAI partnerships OR investors site:techcrunch.com'\n"
        "- 'OpenAI Twitter OR Reddit reputation'\n"
        "- 'OpenAI reviews OR user feedback site:trustpilot.com'\n"
        "- 'OpenAI annual report OR whitepaper filetype:pdf'\n"
        "- 'OpenAI patents OR publications site:google.com/patents'\n"
        "- 'OpenAI careers OR work culture site:glassdoor.com'\n"
        "- 'OpenAI CEO interview OR keynote OR conference'\n\n"
        "Return ONLY the output as a pure JSON list, without any markdown, "
        "backticks, or code block. Do not include ```json or similar. "
        "Output only the JSON list.\n\n"
        "Input: {name}\n"
        "Language: {language}\n"
        "Context: {context}"
    )
)

VERIFIER_PROMPT = PromptTemplate(
    input_variables=["text_chunks", "language"],
    template=(
        "Check the consistency and reliability of the following information "
        "(each item is an excerpt from different sources): {text_chunks} "
        "Reply only 'OK' if everything is consistent, or reply with a JSON "
        "formatted as: "
        "- whys: reasons why the information is not consistent, "
        "  represented as a list "
        "  of sentences (at least one). "
        "- suggested_retry: a search engine query to vary the search for new "
        "  information "
        "  about the mentioned person or company. "
        "Do not include the subject, subject type, or the context previously "
        "provided by the user in the suggested_retry.\n"
        "Example JSON format: {{\"whys\": [\"reason 1\", \"reason 2\"], "
        "\"suggested_retry\": \"social profile linkedin crunchbase\"}}. "
        "Reply in the language {language}."
    )
)

SCORER_PROMPT = PromptTemplate(
    input_variables=["verified_data_log", "language"],
    template=(
        "Use the results (searches) in JSON format to assign a trust score "
        "(0-100),"
        "explaining the reasons clearly, precisely, and positively. "
        "Example of JSON input: {{\"searches\": [\"search text 1\", "
        "\"search text 2\"]}}. "
        "Example of valid JSON output: {{\"score\": 85, "
        "\"details\": \"Reason here\"}}. "
        "Searches: {verified_data_log}. Reply in the language {language}."
    )
)
