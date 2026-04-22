import os
from io import BytesIO

import pandas as pd
import streamlit as st

from src.io_utils import load_dataframe, list_excel_sheets
from src.analyzer import assess_readiness, detect_outliers
from src.ai_assistant import (
    ask_gpt,
    detect_language,
    analyze_dataset_and_generate_questions,
)
from src.charts import missing_chart, outlier_chart
from src.pdf_report import generate_pdf


def get_ui_labels(language="en"):
    if language == "ar":
        return {
            "title": "محلل جودة البيانات بالذكاء الاصطناعي",
            "upload_label": "ارفع ملف CSV أو Excel",
            "analysis_type": "نوع التحليل",
            "analysis_options": {
                "تحليل عام": "general",
                "القيم المفقودة": "missing",
                "القيم الشاذة": "outliers",
                "التكرارات": "duplicates",
            },
            "question_label": "اكتب سؤالك عن البيانات",
            "question_placeholder": "مثال: ما أهم مشاكل الجودة في هذا الملف؟ وما أولويات التنظيف والتحليل؟",
            "sheet_label": "اختر الورقة",
            "preview_title": "معاينة البيانات",
            "score_label": "درجة جودة البيانات",
            "analyze_button": "تحليل",
            "executive_summary": "الملخص التنفيذي",
            "direct_answer": "الإجابة المباشرة",
            "findings": "النتائج",
            "recommendations": "التوصيات",
            "next_steps": "الخطوات التالية",
            "download_pdf": "تحميل تقرير PDF",
            "history_title": "سجل الأسئلة",
            "dataset_info": "معلومات البيانات",
            "rows": "عدد الصفوف",
            "columns": "عدد الأعمدة",
            "missing_ratio": "نسبة القيم المفقودة",
            "duplicate_ratio": "نسبة التكرارات",
            "outlier_ratio": "نسبة القيم الشاذة",
            "empty_columns": "الأعمدة الفارغة",
            "constant_columns": "الأعمدة الثابتة",
            "issues_tab": "مشاكل الجودة",
            "charts_tab": "الرسوم البيانية",
            "data_tab": "البيانات",
            "summary_tab": "ملخص الملف",
            "questions_tab": "الأسئلة المقترحة",
            "file_summary_title": "ملخص الملف",
            "smart_summary": "الملخص الذكي",
            "suggested_questions": "الأسئلة المقترحة",
            "use_question": "استخدام",
            "no_question_warning": "اكتبي سؤالًا أولًا ثم اضغطي تحليل.",
            "file_ready": "تم الاحتفاظ بالملف بنجاح.",
            "api_key_missing": "متغير OPENAI_API_KEY غير موجود.",
            "dataset_type": "نوع البيانات",
            "smart_questions_button": "توليد أسئلة ذكية",
            "business_questions": "أسئلة أعمال وتحليل",
            "quality_questions": "أسئلة جودة البيانات",
            "question_count": "عدد الأسئلة المقترحة",
            "fallback_questions_note": "تم استخدام اقتراحات محلية احتياطية لأن التوليد الذكي لم يُرجع نتائج كافية.",
            "all_suggested_questions": "كل الأسئلة المقترحة",
            "language_label": "لغة الواجهة",
            "language_ar": "العربية",
            "language_en": "English",
            "footer_note": "الأسئلة المقترحة تعتمد على بنية الملف وجودة البيانات ونوعها.",
        }

    return {
        "title": "AI Data Quality Analyst",
        "upload_label": "Upload CSV or Excel",
        "analysis_type": "Analysis Type",
        "analysis_options": {
            "General Analysis": "general",
            "Missing Values": "missing",
            "Outliers": "outliers",
            "Duplicates": "duplicates",
        },
        "question_label": "Ask a question about your data",
        "question_placeholder": "Example: What are the main quality issues in this file and what should be cleaned first?",
        "sheet_label": "Choose sheet",
        "preview_title": "Data Preview",
        "score_label": "Data Quality Score",
        "analyze_button": "Analyze",
        "executive_summary": "Executive Summary",
        "direct_answer": "Direct Answer",
        "findings": "Findings",
        "recommendations": "Recommendations",
        "next_steps": "Next Steps",
        "download_pdf": "Download PDF Report",
        "history_title": "Question History",
        "dataset_info": "Dataset Info",
        "rows": "Rows",
        "columns": "Columns",
        "missing_ratio": "Missing Ratio",
        "duplicate_ratio": "Duplicate Ratio",
        "outlier_ratio": "Outlier Ratio",
        "empty_columns": "Empty Columns",
        "constant_columns": "Constant Columns",
        "issues_tab": "Quality Issues",
        "charts_tab": "Charts",
        "data_tab": "Data",
        "summary_tab": "File Summary",
        "questions_tab": "Suggested Questions",
        "file_summary_title": "File Summary",
        "smart_summary": "Smart Summary",
        "suggested_questions": "Suggested Questions",
        "use_question": "Use",
        "no_question_warning": "Please enter a question first, then click Analyze.",
        "file_ready": "File is stored successfully.",
        "api_key_missing": "OPENAI_API_KEY is missing.",
        "dataset_type": "Dataset Type",
        "smart_questions_button": "Generate Smart Questions",
        "business_questions": "Business & Insight Questions",
        "quality_questions": "Data Quality Questions",
        "question_count": "Suggested Question Count",
        "fallback_questions_note": "A local fallback was used because the smart generator did not return enough results.",
        "all_suggested_questions": "All Suggested Questions",
        "language_label": "UI Language",
        "language_ar": "Arabic",
        "language_en": "English",
        "footer_note": "Suggested questions are based on file structure, data quality, and inferred dataset type.",
    }


def summarize_context(df, issues, outliers, max_columns=12, max_outlier_cols=10):
    column_names = df.columns.tolist()[:max_columns]
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.head(max_columns).items()}
    outlier_items = list(outliers.items())[:max_outlier_cols]

    context = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names_sample": column_names,
        "dtypes_sample": dtypes,
        "missing_ratio": round(float(issues["missing_ratio"]), 4),
        "duplicate_ratio": round(float(issues["duplicate_ratio"]), 4),
        "outlier_ratio": round(float(issues["outlier_ratio"]), 4),
        "empty_columns": issues["empty_columns"][:10],
        "constant_columns": issues["constant_columns"][:10],
        "outliers_sample": dict(outlier_items),
        "sample_rows": df.head(3).fillna("").astype(str).to_dict(orient="records"),
    }
    return str(context)


def build_file_profile(df: pd.DataFrame):
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    datetime_columns = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "top_columns": df.columns.tolist()[:15],
        "numeric_columns": numeric_columns[:15],
        "categorical_columns": categorical_columns[:15],
        "datetime_columns": datetime_columns[:10],
    }


def generate_file_summary_text(profile, issues, language="en"):
    rows = profile.get("rows", 0)
    cols = profile.get("columns", 0)
    numeric_cols = profile.get("numeric_columns", [])
    categorical_cols = profile.get("categorical_columns", [])
    datetime_cols = profile.get("datetime_columns", [])

    if language == "ar":
        parts = [
            f"الملف يحتوي على {rows} صفًا و{cols} عمودًا.",
            f"الأعمدة الرقمية: {len(numeric_cols)}، والأعمدة النصية/الفئوية: {len(categorical_cols)}، وأعمدة التاريخ/الوقت: {len(datetime_cols)}.",
            f"نسبة القيم المفقودة: {issues['missing_ratio']:.2%}، ونسبة التكرارات: {issues['duplicate_ratio']:.2%}، ونسبة القيم الشاذة: {issues['outlier_ratio']:.2%}.",
        ]
        if issues["empty_columns"]:
            parts.append(f"توجد أعمدة فارغة بالكامل: {', '.join(issues['empty_columns'][:5])}.")
        if issues["constant_columns"]:
            parts.append(f"وتوجد أعمدة ثابتة القيم: {', '.join(issues['constant_columns'][:5])}.")
        return " ".join(parts)

    parts = [
        f"The file contains {rows} rows and {cols} columns.",
        f"It includes {len(numeric_cols)} numeric columns, {len(categorical_cols)} categorical/text columns, and {len(datetime_cols)} date/time columns.",
        f"Missing ratio: {issues['missing_ratio']:.2%}, duplicate ratio: {issues['duplicate_ratio']:.2%}, outlier ratio: {issues['outlier_ratio']:.2%}.",
    ]
    if issues["empty_columns"]:
        parts.append(f"Fully empty columns found: {', '.join(issues['empty_columns'][:5])}.")
    if issues["constant_columns"]:
        parts.append(f"Constant-value columns found: {', '.join(issues['constant_columns'][:5])}.")
    return " ".join(parts)


def normalize_arabic_text(text: str) -> str:
    if not text:
        return ""
    replacements = {
        "dataset": "مجموعة البيانات",
        "missing values": "القيم المفقودة",
        "outliers": "القيم الشاذة",
        "duplicates": "السجلات المكررة",
        "data quality": "جودة البيانات",
    }
    cleaned = text
    for src, dst in replacements.items():
        cleaned = cleaned.replace(src, dst)
        cleaned = cleaned.replace(src.title(), dst)
    return cleaned.strip()


def estimate_question_count(df: pd.DataFrame) -> int:
    rows, cols = df.shape
    score = 0

    if rows >= 20000:
        score += 3
    elif rows >= 1000:
        score += 2
    else:
        score += 1

    if cols >= 25:
        score += 3
    elif cols >= 8:
        score += 2
    else:
        score += 1

    numeric_cols = df.select_dtypes(include="number").shape[1]
    object_cols = df.select_dtypes(include=["object", "string", "category"]).shape[1]

    if numeric_cols >= 8:
        score += 2
    if object_cols >= 8:
        score += 1

    missing_ratio = float(df.isnull().sum().sum()) / max(1, (df.shape[0] * df.shape[1]))
    if missing_ratio > 0.05:
        score += 1

    if score <= 4:
        return 6
    if score <= 7:
        return 10
    return 14


def detect_dataset_type_rule_based(profile) -> str:
    cols = [str(c).lower() for c in profile.get("top_columns", [])]
    cols += [str(c).lower() for c in profile.get("numeric_columns", [])[:10]]
    cols += [str(c).lower() for c in profile.get("categorical_columns", [])[:10]]
    joined = " ".join(cols)

    rules = {
        "sales": [
            "sales", "revenue", "product", "customer", "order", "price", "quantity", "invoice",
            "client", "deal", "amount"
        ],
        "hr": [
            "employee", "salary", "department", "manager", "hire", "attrition", "staff",
            "payroll", "designation", "job_title"
        ],
        "finance": [
            "expense", "profit", "budget", "cost", "ledger", "account", "payment",
            "balance", "cash", "transaction"
        ],
        "operations": [
            "process", "status", "duration", "cycle", "task", "ticket", "sla",
            "throughput", "queue", "operation"
        ],
        "marketing": [
            "campaign", "channel", "click", "impression", "lead", "conversion", "ctr",
            "cpc", "roas", "engagement"
        ],
        "customer_support": [
            "case", "ticket", "resolution", "agent", "priority", "support", "response_time",
            "csat", "complaint"
        ],
        "inventory": [
            "stock", "warehouse", "sku", "inventory", "supplier", "reorder", "shipment",
            "unit_cost", "item"
        ],
    }

    best_type = "unknown"
    best_score = 0

    for dataset_type, keywords in rules.items():
        score = sum(1 for keyword in keywords if keyword in joined)
        if score > best_score:
            best_score = score
            best_type = dataset_type

    if best_score == 0:
        return "unknown"
    return best_type


def generate_local_fallback_questions(df, issues, profile, language="en"):
    dataset_type = detect_dataset_type_rule_based(profile)
    question_count = estimate_question_count(df)

    top_cols = ", ".join(profile["top_columns"][:5]) if profile["top_columns"] else ""
    numeric_cols = ", ".join(profile["numeric_columns"][:4]) if profile["numeric_columns"] else ""
    cat_cols = ", ".join(profile["categorical_columns"][:4]) if profile["categorical_columns"] else ""

    if language == "ar":
        common = [
            "ما الذي يحتويه هذا الملف بشكل عام، وما أهم الأعمدة التي يعتمد عليها التحليل؟",
            "ما أبرز مشاكل جودة البيانات في هذا الملف، وما أثرها على التحليل؟",
            "ما الأعمدة التي يجب تنظيفها أولًا قبل استخدام البيانات في التقارير أو النماذج؟",
            "هل توجد قيم مفقودة أو سجلات مكررة أو أعمدة ثابتة قد تقلل موثوقية النتائج؟",
            "ما المؤشرات أو العلاقات الأولية التي يمكن استخراجها من هذه البيانات؟",
            f"اشرح دور هذه الأعمدة باختصار: {top_cols}" if top_cols else "ما الأعمدة الأكثر أهمية في هذا الملف؟",
        ]

        domain_map = {
            "sales": [
                "ما المنتجات أو العملاء أو المناطق التي تحقق أفضل أداء؟",
                "هل توجد أنماط زمنية أو موسمية في المبيعات؟",
                "هل توجد منتجات أو فئات ضعيفة الأداء تحتاج مراجعة؟",
            ],
            "hr": [
                "هل توجد فروقات واضحة بين الأقسام أو الوظائف أو الرواتب؟",
                "ما المؤشرات التي قد تدل على attrition أو مشاكل توزيع الموارد؟",
                "هل هناك حقول ناقصة في بيانات الموظفين قد تؤثر على التحليل؟",
            ],
            "finance": [
                "ما أكبر مصادر المصروفات أو الانحرافات المالية؟",
                "هل توجد معاملات شاذة أو قيود تحتاج مراجعة؟",
                "ما أبرز مؤشرات الربحية أو التوازن المالي في الملف؟",
            ],
            "operations": [
                "أين توجد الاختناقات أو التأخيرات في العمليات؟",
                "ما المراحل أو الحالات التي تستغرق وقتًا أطول من المتوقع؟",
                "هل توجد أنماط تشغيلية متكررة تشير إلى ضعف كفاءة؟",
            ],
            "marketing": [
                "ما القنوات أو الحملات الأعلى أداءً؟",
                "هل توجد حملات ذات تكلفة مرتفعة وعائد ضعيف؟",
                "ما العوامل الأكثر ارتباطًا بالتحويل أو التفاعل؟",
            ],
            "customer_support": [
                "ما أنواع الحالات أو التذاكر الأكثر تكرارًا؟",
                "هل توجد أنماط مرتبطة بتأخر الإغلاق أو انخفاض الرضا؟",
                "ما أولويات التحسين في تجربة الدعم؟",
            ],
            "inventory": [
                "ما الأصناف المعرضة لنفاد المخزون أو ضعف الدوران؟",
                "هل توجد اختلافات واضحة بين المواقع أو الموردين؟",
                "ما المؤشرات التي تساعد على تحسين قرارات التخزين وإعادة الطلب؟",
            ],
            "unknown": [
                "ما أهم 3 أسئلة تحليلية ينبغي البدء بها لفهم هذا الملف؟",
                "ما الجوانب الأكثر خطورة في جودة البيانات هنا؟",
                "ما المؤشرات التي تستحق عرضها في dashboard؟",
            ],
        }

        quality = [
            f"هل توجد قيم شاذة في الأعمدة الرقمية التالية: {numeric_cols}؟" if numeric_cols else "هل توجد قيم شاذة قد تؤثر على التحليل؟",
            f"ما الأنماط أو الفئات الأكثر تكرارًا في الأعمدة التالية: {cat_cols}؟" if cat_cols else "ما الفئات أو الأنماط الأكثر تكرارًا في الملف؟",
            f"هل نسبة القيم المفقودة الحالية ({issues['missing_ratio']:.1%}) تؤثر على موثوقية النتائج؟",
            f"هل نسبة التكرار الحالية ({issues['duplicate_ratio']:.1%}) تستدعي تنظيفًا قبل التحليل؟",
        ]

        all_questions = common + domain_map.get(dataset_type, domain_map["unknown"]) + quality
        return {
            "dataset_type": dataset_type,
            "summary": generate_file_summary_text(profile, issues, language="ar"),
            "questions": all_questions[:question_count],
            "business_questions": domain_map.get(dataset_type, domain_map["unknown"]),
            "quality_questions": quality,
        }

    common = [
        "What does this file contain overall, and which columns are most important for analysis?",
        "What are the main data quality issues in this file, and how do they affect trust in the analysis?",
        "Which columns should be cleaned first before using this dataset in reports or models?",
        "Are there missing values, duplicates, or constant columns reducing reliability?",
        "What initial patterns or relationships can be extracted from this dataset?",
        f"Explain the likely role of these columns: {top_cols}" if top_cols else "Which columns seem most important in this dataset?",
    ]

    domain_map = {
        "sales": [
            "Which products, customers, or regions perform best?",
            "Are there time-based or seasonal patterns in sales?",
            "Are there underperforming products or categories that need review?",
        ],
        "hr": [
            "Are there clear differences across departments, roles, or salaries?",
            "What signals may indicate attrition or workforce imbalance?",
            "Are there missing employee fields that weaken HR analysis?",
        ],
        "finance": [
            "What are the largest sources of cost or financial variance?",
            "Are there anomalous transactions that need review?",
            "What are the strongest indicators of profitability or imbalance?",
        ],
        "operations": [
            "Where are the bottlenecks or delays in the process?",
            "Which stages or statuses take longer than expected?",
            "Are there repeated operational patterns indicating inefficiency?",
        ],
        "marketing": [
            "Which channels or campaigns perform best?",
            "Are there campaigns with high cost and weak return?",
            "What factors are most associated with conversion or engagement?",
        ],
        "customer_support": [
            "What ticket types or cases appear most often?",
            "Are there patterns related to slow resolution or low satisfaction?",
            "What should be prioritized to improve support performance?",
        ],
        "inventory": [
            "Which items are at risk of stockout or low turnover?",
            "Are there meaningful differences across sites or suppliers?",
            "What indicators could improve stocking and reorder decisions?",
        ],
        "unknown": [
            "What are the top 3 questions I should start with to understand this dataset?",
            "What are the riskiest data quality weaknesses here?",
            "What metrics are most suitable for a dashboard?",
        ],
    }

    quality = [
        f"Are there outliers in these numeric columns: {numeric_cols}?" if numeric_cols else "Are there outliers that could distort analysis?",
        f"What patterns or repeated categories exist in these columns: {cat_cols}?" if cat_cols else "What are the most repeated categories or patterns in the dataset?",
        f"Does the current missing-value ratio ({issues['missing_ratio']:.1%}) weaken analytical confidence?",
        f"Does the current duplicate ratio ({issues['duplicate_ratio']:.1%}) require cleanup before analysis?",
    ]

    all_questions = common + domain_map.get(dataset_type, domain_map["unknown"]) + quality
    return {
        "dataset_type": dataset_type,
        "summary": generate_file_summary_text(profile, issues, language="en"),
        "questions": all_questions[:question_count],
        "business_questions": domain_map.get(dataset_type, domain_map["unknown"]),
        "quality_questions": quality,
    }


def build_ai_question_payload(df, issues, profile):
    sample_rows = df.head(5).fillna("").astype(str).to_dict(orient="records")
    payload = {
        "file_profile": profile,
        "quality_issues": {
            "missing_ratio": round(float(issues["missing_ratio"]), 4),
            "duplicate_ratio": round(float(issues["duplicate_ratio"]), 4),
            "outlier_ratio": round(float(issues["outlier_ratio"]), 4),
            "empty_columns": issues["empty_columns"][:10],
            "constant_columns": issues["constant_columns"][:10],
        },
        "column_names": df.columns.tolist()[:30],
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample_rows": sample_rows,
    }
    return str(payload)


def build_suggested_questions(df, issues, profile, language="en"):
    """
    1) Tries AI-based dataset understanding + dynamic question generation
    2) Falls back to local domain-aware question generation
    """
    target_question_count = estimate_question_count(df)
    ai_context = build_ai_question_payload(df, issues, profile)

    try:
        result = analyze_dataset_and_generate_questions(
            dataset_context=ai_context,
            language=language,
            target_question_count=target_question_count,
        )

        questions = result.get("questions", []) or []
        business_questions = result.get("business_questions", []) or []
        quality_questions = result.get("quality_questions", []) or []
        dataset_type = result.get("dataset_type", "unknown") or "unknown"
        summary = result.get("summary", "")

        if language == "ar":
            questions = [normalize_arabic_text(q) for q in questions]
            business_questions = [normalize_arabic_text(q) for q in business_questions]
            quality_questions = [normalize_arabic_text(q) for q in quality_questions]
            summary = normalize_arabic_text(summary)

        if len(questions) >= max(5, target_question_count // 2):
            return {
                "dataset_type": dataset_type,
                "summary": summary,
                "questions": questions[:target_question_count],
                "business_questions": business_questions[: max(3, target_question_count // 2)],
                "quality_questions": quality_questions[: max(3, target_question_count // 3)],
                "used_fallback": False,
            }
    except Exception:
        pass

    fallback_result = generate_local_fallback_questions(df, issues, profile, language=language)
    fallback_result["used_fallback"] = True
    return fallback_result


def init_session_state():
    defaults = {
        "history": [],
        "last_language": "en",
        "ui_language": "ar",
        "uploaded_file_name": None,
        "uploaded_file_bytes": None,
        "selected_sheet": None,
        "latest_result": None,
        "latest_outliers": None,
        "latest_df": None,
        "latest_issues": None,
        "file_summary_result": None,
        "file_profile": None,
        "smart_questions_result": None,
        "dataset_type": "unknown",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_uploaded_file_from_session():
    file_bytes = st.session_state.get("uploaded_file_bytes")
    file_name = st.session_state.get("uploaded_file_name")

    if not file_bytes or not file_name:
        return None

    buffer = BytesIO(file_bytes)
    buffer.name = file_name
    return buffer


st.set_page_config(page_title="AI Data Quality Analyst", layout="wide")
init_session_state()

current_language = st.session_state.get("ui_language", "ar")
ui = get_ui_labels(current_language)

st.title(ui["title"])

if not os.getenv("OPENAI_API_KEY"):
    st.error(ui["api_key_missing"])
    st.stop()

with st.sidebar:
    st.subheader(ui["language_label"])
    language_choice = st.radio(
        ui["language_label"],
        options=["ar", "en"],
        format_func=lambda x: ui["language_ar"] if x == "ar" else ui["language_en"],
        index=0 if current_language == "ar" else 1,
        key="ui_language_radio",
    )
    st.session_state["ui_language"] = language_choice
    current_language = language_choice
    ui = get_ui_labels(current_language)

with st.sidebar:
    st.subheader(ui["analysis_type"])
    analysis_label = st.selectbox(
        ui["analysis_type"],
        list(ui["analysis_options"].keys()),
        key="analysis_type_select",
    )
    analysis_type = ui["analysis_options"][analysis_label]

uploaded_file = st.file_uploader(
    ui["upload_label"],
    type=["csv", "xlsx"],
    key="file_upload",
)

if uploaded_file is not None:
    st.session_state["uploaded_file_name"] = uploaded_file.name
    st.session_state["uploaded_file_bytes"] = uploaded_file.getvalue()
    st.session_state["latest_result"] = None
    st.session_state["latest_outliers"] = None
    st.session_state["latest_df"] = None
    st.session_state["latest_issues"] = None
    st.session_state["file_profile"] = None
    st.session_state["smart_questions_result"] = None
    st.session_state["dataset_type"] = "unknown"

uploaded = get_uploaded_file_from_session()

question = st.text_input(
    ui["question_label"],
    key="question_input",
    placeholder=ui["question_placeholder"],
)

if uploaded is not None:
    st.success(ui["file_ready"])

    if uploaded.name.lower().endswith(".xlsx"):
        sheet_source = BytesIO(st.session_state["uploaded_file_bytes"])
        sheet_source.name = st.session_state["uploaded_file_name"]
        sheets = list_excel_sheets(sheet_source)

        default_index = 0
        if st.session_state["selected_sheet"] in sheets:
            default_index = sheets.index(st.session_state["selected_sheet"])

        selected_sheet = st.selectbox(
            ui["sheet_label"],
            sheets,
            index=default_index,
            key="sheet_select",
        )
        st.session_state["selected_sheet"] = selected_sheet

        data_source = BytesIO(st.session_state["uploaded_file_bytes"])
        data_source.name = st.session_state["uploaded_file_name"]
        df = load_dataframe(data_source, sheet_name=selected_sheet)
    else:
        data_source = BytesIO(st.session_state["uploaded_file_bytes"])
        data_source.name = st.session_state["uploaded_file_name"]
        df = load_dataframe(data_source)

    score, issues = assess_readiness(df)
    outliers = detect_outliers(df)
    file_profile = build_file_profile(df)

    st.session_state["file_profile"] = file_profile

    smart_questions_result = build_suggested_questions(df, issues, file_profile, current_language)
    st.session_state["smart_questions_result"] = smart_questions_result
    st.session_state["dataset_type"] = smart_questions_result.get("dataset_type", "unknown")

    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader(ui["preview_title"])
        st.dataframe(df.head())

    with right_col:
        st.subheader(ui["dataset_info"])
        st.metric(ui["score_label"], score)
        st.write(f"**{ui['rows']}:** {df.shape[0]}")
        st.write(f"**{ui['columns']}:** {df.shape[1]}")
        st.write(f"**{ui['missing_ratio']}:** {issues['missing_ratio']:.2%}")
        st.write(f"**{ui['duplicate_ratio']}:** {issues['duplicate_ratio']:.2%}")
        st.write(f"**{ui['outlier_ratio']}:** {issues['outlier_ratio']:.2%}")

    tabs = st.tabs([
        ui["summary_tab"],
        ui["questions_tab"],
        ui["charts_tab"],
        ui["data_tab"],
    ])

    with tabs[0]:
        st.subheader(ui["file_summary_title"])

        smart_result = st.session_state.get("smart_questions_result") or {}
        smart_summary = smart_result.get("summary", "")
        dataset_type = st.session_state.get("dataset_type", "unknown")

        summary_text = smart_summary or generate_file_summary_text(file_profile, issues, current_language)
        st.info(summary_text)

        st.write(f"**{ui['dataset_type']}:** {dataset_type}")
        st.write(f"**{ui['question_count']}:** {estimate_question_count(df)}")

    with tabs[1]:
        st.subheader(ui["suggested_questions"])

        smart_result = st.session_state.get("smart_questions_result") or {}
        all_questions = smart_result.get("questions", [])
        business_questions = smart_result.get("business_questions", [])
        quality_questions = smart_result.get("quality_questions", [])
        used_fallback = smart_result.get("used_fallback", False)

        if used_fallback:
            st.caption(ui["fallback_questions_note"])

        if business_questions:
            st.markdown(f"### {ui['business_questions']}")
            for idx, suggested_question in enumerate(business_questions):
                q_col, btn_col = st.columns([5, 1])
                q_col.write(f"- {suggested_question}")
                if btn_col.button(ui["use_question"], key=f"use_business_question_{idx}"):
                    st.session_state["question_input"] = suggested_question
                    st.rerun()

        if quality_questions:
            st.markdown(f"### {ui['quality_questions']}")
            for idx, suggested_question in enumerate(quality_questions):
                q_col, btn_col = st.columns([5, 1])
                q_col.write(f"- {suggested_question}")
                if btn_col.button(ui["use_question"], key=f"use_quality_question_{idx}"):
                    st.session_state["question_input"] = suggested_question
                    st.rerun()

        if all_questions:
            st.markdown(f"### {ui['all_suggested_questions']}")
            for idx, suggested_question in enumerate(all_questions):
                q_col, btn_col = st.columns([5, 1])
                q_col.write(f"- {suggested_question}")
                if btn_col.button(ui["use_question"], key=f"use_question_{idx}"):
                    st.session_state["question_input"] = suggested_question
                    st.rerun()

        st.caption(ui["footer_note"])

    with tabs[2]:
        st.pyplot(missing_chart(df, language=current_language))
        st.pyplot(outlier_chart(outliers, language=current_language))

    with tabs[3]:
        st.dataframe(df)

    if st.button(ui["analyze_button"], use_container_width=True, key="analyze_button"):
        if not question.strip():
            st.warning(ui["no_question_warning"])
        else:
            language = current_language
            st.session_state["last_language"] = language

            context = summarize_context(df, issues, outliers)
            result = ask_gpt(question, context, analysis_type, language=language)
            result["_language"] = language

            st.session_state["history"].append((question, result))
            st.session_state["history"] = st.session_state["history"][-5:]

            st.session_state["latest_result"] = result
            st.session_state["latest_outliers"] = outliers
            st.session_state["latest_df"] = df
            st.session_state["latest_issues"] = issues

if st.session_state.get("latest_result") is not None:
    result = st.session_state["latest_result"]
    language = result.get("_language", st.session_state["last_language"])
    ui = get_ui_labels(language)

    outliers = st.session_state["latest_outliers"]
    df = st.session_state["latest_df"]
    issues = st.session_state["latest_issues"]

    st.subheader(ui["executive_summary"])
    st.write(result.get("executive_summary", ""))

    st.subheader(ui["direct_answer"])
    st.write(result.get("direct_answer", ""))

    tab1, tab2, tab3 = st.tabs([ui["issues_tab"], ui["charts_tab"], ui["data_tab"]])

    with tab1:
        st.subheader(ui["findings"])
        findings = result.get("findings", [])
        if findings:
            for item in findings:
                st.write(f"- {item}")

        st.subheader(ui["recommendations"])
        recommendations = result.get("recommendations", [])
        if recommendations:
            for item in recommendations:
                st.write(f"- {item}")

        next_steps = result.get("next_steps", [])
        if next_steps:
            st.subheader(ui["next_steps"])
            for item in next_steps:
                st.write(f"- {item}")

        st.write(f"**{ui['empty_columns']}:** {issues['empty_columns']}")
        st.write(f"**{ui['constant_columns']}:** {issues['constant_columns']}")

    with tab2:
        st.pyplot(missing_chart(df, language=language))
        st.pyplot(outlier_chart(outliers, language=language))

    with tab3:
        st.dataframe(df)

    pdf = generate_pdf(result)

    st.download_button(
        ui["download_pdf"],
        pdf,
        file_name="report.pdf",
        mime="application/pdf",
        key="download_pdf_button",
    )

with st.sidebar:
    st.subheader(ui["history_title"])
    for q, _ in st.session_state["history"][-5:]:
        st.write(f"- {q}")
