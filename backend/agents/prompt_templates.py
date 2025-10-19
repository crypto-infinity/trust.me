"""
Prompt templates for TrustME agents.
"""

from langchain.prompts import PromptTemplate

QUERY_DEFINER_PROMPT = PromptTemplate(
    input_variables=["name", "language", "context", "top_k"],
    template=(
        "You are an OSINT research agent. "
        "You receive as input the name of a company or individual "
        "(e.g., 'OpenAI', 'Gabriele Scorpaniti') and some context. "
        "Your task is to generate a list of search queries, in the specified "
        "language and optimized for Serper Api, tailored to the type of the "
        "input provided. Generate at least {top_k} queries.\n\n"
        "Generate one query string ready to be used with Serper Api. Queries "
        "should include Boolean operators, quotation marks for exact phrases,"
        "and specific "
        "keywords to increase precision. If the subject is a person, adapt the"
        " categories accordingly. Use the context only if relevant.\n\n"
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
        "Analyze the following excerpts of information from different sources:"
        "{text_chunks}. "
        "Assess whether the information is consistent, reliable,"
        " and free of contradictions. "
        "If everything is consistent, reply only 'OK'. "
        "If you find discrepancies, reply with a JSON containing: "
        "- whys: a list of contradictions or reasons for doubt (at least one)."
        "- suggested_retry: a search engine query to clarify the critical "
        "points and to find additional information for a more complete "
        "verification. "
        "Do not include the subject, subject type, or the context previously "
        "provided by the user in suggested_retry.\n"
        "Example: {{\"whys\": [\"Reason 1\", \"Reason 2\"],"
        " \"suggested_retry\": \"keywords for new search\"}}. "
        "Reply in language {language}."
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
