import json
from openai import OpenAI

client = OpenAI()


def detect_language(text: str) -> str:
    if not text:
        return "en"

    arabic_chars = sum(1 for ch in text if "\u0600" <= ch <= "\u06FF")
    english_chars = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))

    if arabic_chars > english_chars:
        return "ar"
    return "en"



def ask_gpt(question, dataset_context, analysis_type="general", language=None):
    language = language or detect_language(question)

    if language == "ar":
        language_instruction = """
IMPORTANT:
- Respond in Arabic.
- Use clear professional Arabic.
- Keep the JSON keys in English exactly as provided.
- Be concise but useful.
"""
    else:
        language_instruction = """
IMPORTANT:
- Respond in English.
- Use clear professional English.
- Keep the JSON keys in English exactly as provided.
- Be concise but useful.
"""

    system_prompt = f"""
You are an expert data quality analyst.

Return your response STRICTLY as valid JSON with this structure:

{{
  "executive_summary": "...",
  "direct_answer": "...",
  "findings": ["..."],
  "recommendations": ["..."],
  "next_steps": ["..."]
}}

{language_instruction}
Base your answer only on the dataset context provided.
Do not add markdown fences.
Do not add extra text outside the JSON.
"""

    prompt = f"""
DATASET CONTEXT:
{dataset_context}

USER QUESTION:
{question}

ANALYSIS TYPE:
{analysis_type}
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    text = response.output_text.strip()

    try:
        result = json.loads(text)
    except Exception:
        result = {
            "executive_summary": text,
            "direct_answer": text,
            "findings": [],
            "recommendations": [],
            "next_steps": [],
        }

    result["_language"] = language
    return result
