import json
from typing import Any, Dict

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


def _safe_json_loads(text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        return fallback


def _language_instruction(language: str) -> str:
    if language == "ar":
        return """
IMPORTANT:
- Respond in Arabic.
- Use clear, natural, professional Arabic.
- Avoid literal translation from English.
- Keep the JSON keys in English exactly as provided.
- Be concise but useful.
"""
    return """
IMPORTANT:
- Respond in English.
- Use clear professional English.
- Keep the JSON keys in English exactly as provided.
- Be concise but useful.
"""


def ask_gpt(question, dataset_context, analysis_type="general", language=None):
    language = language or detect_language(question)

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

{_language_instruction(language)}
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

    result = _safe_json_loads(
        text,
        {
            "executive_summary": text,
            "direct_answer": text,
            "findings": [],
            "recommendations": [],
            "next_steps": [],
        },
    )

    result["_language"] = language
    return result


def analyze_dataset_and_generate_questions(
    dataset_context: str,
    language: str = "ar",
    target_question_count: int = 10,
) -> Dict[str, Any]:
    """
    Uses AI to:
    1) infer dataset type
    2) summarize the file
    3) generate dynamic, deeper questions
    """

    if language == "ar":
        extra_instruction = """
- اكتب العربية بصياغة طبيعية وفصحى واضحة.
- لا تستخدم ترجمة حرفية ركيكة.
- اجعل الأسئلة عميقة، عملية، ومفيدة لقرار أعمال وتحليل جودة البيانات.
- نوّع الأسئلة بين:
  1) فهم الملف
  2) جودة البيانات
  3) التحليل التجاري/العملي
  4) المخاطر أو القيم الشاذة
  5) أولويات التنظيف
"""
        fallback_summary = "تعذر توليد ملخص ذكي حاليًا."
    else:
        extra_instruction = """
- Write clear natural English.
- Make the questions deep, practical, and useful for both business analysis and data quality review.
- Diversify questions across:
  1) understanding the file
  2) data quality
  3) business/operational insights
  4) anomalies and risks
  5) cleaning priorities
"""
        fallback_summary = "Could not generate a smart summary right now."

    system_prompt = f"""
You are a senior data analyst and data quality expert.

Return STRICTLY valid JSON using exactly this structure:

{{
  "dataset_type": "...",
  "summary": "...",
  "questions": ["..."],
  "business_questions": ["..."],
  "quality_questions": ["..."]
}}

Rules:
- Infer the dataset type from the provided context.
- The dataset_type should be one of:
  sales, hr, finance, operations, marketing, customer_support, inventory, mixed, unknown
- Create approximately {target_question_count} questions in total.
- Questions must be based on the actual dataset context, not generic templates.
- Keep the JSON keys in English exactly as provided.
- Do not add markdown.
- Do not add any text outside JSON.
{_language_instruction(language)}
{extra_instruction}
"""

    user_prompt = f"""
DATASET CONTEXT:
{dataset_context}
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = response.output_text.strip()

    result = _safe_json_loads(
        text,
        {
            "dataset_type": "unknown",
            "summary": fallback_summary,
            "questions": [],
            "business_questions": [],
            "quality_questions": [],
        },
    )

    result["_language"] = language
    return result
