import os
from io import BytesIO

import pandas as pd
import streamlit as st

from src.io_utils import load_dataframe, list_excel_sheets
from src.analyzer import assess_readiness, detect_outliers
from src.ai_assistant import ask_gpt
from src.charts import missing_chart, outlier_chart
from src.pdf_report import generate_pdf


TRANSLATIONS = {
    "ar": {
        "page_title": "محلل جودة البيانات بالذكاء الاصطناعي",
        "title": "محلل جودة البيانات بالذكاء الاصطناعي",
        "subtitle": "حلّل ملفات CSV وExcel، افهم الجودة بسرعة، واسأل الذكاء الاصطناعي عن بياناتك.",
        "language": "لغة الواجهة",
        "language_options": {"العربية": "ar", "English": "en"},
        "upload_label": "ارفع ملف CSV أو Excel",
        "analysis_type": "نوع التحليل",
        "analysis_options": {
            "تحليل عام": "general",
            "القيم المفقودة": "missing",
            "القيم الشاذة": "outliers",
            "التكرارات": "duplicates",
        },
        "question_label": "اكتب سؤالك عن البيانات",
        "question_placeholder": "مثال: ما أهم مشاكل الجودة في هذا الملف؟",
        "sheet_label": "اختر الورقة",
        "preview_title": "معاينة البيانات",
        "score_label": "درجة جودة البيانات",
        "analyze_button": "تحليل بالسؤال المكتوب",
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
        "suggestions_tab": "أسئلة مقترحة",
        "no_question_warning": "اكتبي سؤالًا أولًا ثم اضغطي تحليل.",
        "file_ready": "تم رفع الملف بنجاح.",
        "api_key_missing": "متغير OPENAI_API_KEY غير موجود.",
        "file_summary_title": "ملخص الملف وماذا يحتوي",
        "file_name": "اسم الملف",
        "file_type": "نوع الملف",
        "sheet_count": "عدد الأوراق",
        "numeric_columns": "الأعمدة الرقمية",
        "categorical_columns": "الأعمدة النصية/الفئوية",
        "date_columns": "أعمدة التاريخ المحتملة",
        "top_columns": "أبرز الأعمدة",
        "sample_values": "أمثلة من القيم",
        "suggested_questions": "أسئلة ممكن تسألينها عن هذه البيانات",
        "use_question": "استخدام هذا السؤال",
        "auto_summary_button": "إنشاء ملخص ذكي للملف",
        "profile_title": "بطاقة الملف",
        "quality_snapshot": "لقطة سريعة عن الجودة",
        "no_sheet": "ورقة واحدة",
        "ask_ai_hint": "اكتبي سؤالًا أو اختاري واحدًا من المقترحات أدناه.",
        "analysis_ready": "التحليل جاهز",
        "footer_note": "الاقتراحات مبنية على بنية الملف وجودة البيانات الحالية.",
        "summary_intro": "هذا الملف يحتوي على",
    },
    "en": {
        "page_title": "AI Data Quality Analyst",
        "title": "AI Data Quality Analyst",
        "subtitle": "Analyze CSV and Excel files, understand data quality fast, and ask AI about your dataset.",
        "language": "Interface Language",
        "language_options": {"Arabic": "ar", "English": "en"},
        "upload_label": "Upload CSV or Excel",
        "analysis_type": "Analysis Type",
        "analysis_options": {
            "General Analysis": "general",
            "Missing Values": "missing",
            "Outliers": "outliers",
            "Duplicates": "duplicates",
        },
        "question_label": "Ask a question about your data",
        "question_placeholder": "Example: What are the main quality issues in this file?",
        "sheet_label": "Choose sheet",
        "preview_title": "Data Preview",
        "score_label": "Data Quality Score",
        "analyze_button": "Analyze with this question",
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
        "suggestions_tab": "Suggested Questions",
        "no_question_warning": "Please enter a question first, then click Analyze.",
        "file_ready": "File uploaded successfully.",
        "api_key_missing": "OPENAI_API_KEY is missing.",
        "file_summary_title": "File summary and contents",
        "file_name": "File name",
        "file_type": "File type",
        "sheet_count": "Sheet count",
        "numeric_columns": "Numeric columns",
        "categorical_columns": "Text/Categorical columns",
        "date_columns": "Potential date columns",
        "top_columns": "Key columns",
        "sample_values": "Sample values",
        "suggested_questions": "Questions you can ask about this dataset",
        "use_question": "Use this question",
        "auto_summary_button": "Generate smart file summary",
        "profile_title": "File Card",
        "quality_snapshot": "Quality Snapshot",
        "no_sheet": "Single sheet",
        "ask_ai_hint": "Write a question or choose one from the suggestions below.",
        "analysis_ready": "Analysis ready",
        "footer_note": "Suggestions are based on the file structure and current data quality profile.",
        "summary_intro": "This file contains",
    },
}


def get_ui_labels(language="en"):
    return TRANSLATIONS.get(language, TRANSLATIONS["en"])


def detect_language(text: str) -> str:
    if not text:
        return "en"
    arabic_chars = sum(1 for ch in text if "\u0600" <= ch <= "\u06FF")
    english_chars = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))
    return "ar" if arabic_chars > english_chars else "en"


def summarize_context(df, issues, outliers, file_profile, max_columns=15, max_outlier_cols=10):
    column_names = df.columns.tolist()[:max_columns]
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.head(max_columns).items()}
    outlier_items = list(outliers.items())[:max_outlier_cols]

    context = {
        "file_profile": file_profile,
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


def init_session_state():
    defaults = {
        "history": [],
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


def build_file_profile(df: pd.DataFrame, file_name: str, selected_sheet=None, sheet_count=1):
    inferred_dates = [
        col for col in df.columns
        if "date" in str(col).lower() or "time" in str(col).lower()
    ]
    object_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    sample_values = {}
    for col in df.columns[:8]:
        values = [str(v) for v in df[col].dropna().astype(str).head(3).tolist()]
        sample_values[col] = values

    return {
        "file_name": file_name,
        "file_type": file_name.split(".")[-1].upper() if "." in file_name else "Unknown",
        "selected_sheet": selected_sheet,
        "sheet_count": sheet_count,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "numeric_columns": numeric_cols,
        "categorical_columns": object_cols,
        "date_columns": inferred_dates,
        "top_columns": df.columns.tolist()[:10],
        "sample_values": sample_values,
    }


def generate_file_summary_text(profile, issues, language="en"):
    rows = profile["rows"]
    cols = profile["columns"]
    numeric_count = len(profile["numeric_columns"])
    categorical_count = len(profile["categorical_columns"])
    date_count = len(profile["date_columns"])
    key_columns = ", ".join(profile["top_columns"][:5]) if profile["top_columns"] else "-"

    if language == "ar":
        return (
            f"هذا الملف يحتوي على {rows} صف و{cols} عمود. "
            f"فيه {numeric_count} أعمدة رقمية و{categorical_count} أعمدة نصية/فئوية"
            f" و{date_count} أعمدة تبدو كتواريخ. "
            f"أبرز الأعمدة: {key_columns}. "
            f"حاليًا نسبة القيم المفقودة {issues['missing_ratio']:.1%}، "
            f"ونسبة التكرارات {issues['duplicate_ratio']:.1%}، "
            f"ونسبة القيم الشاذة التقديرية {issues['outlier_ratio']:.1%}."
        )
    return (
        f"This file contains {rows} rows and {cols} columns. "
        f"It has {numeric_count} numeric columns, {categorical_count} text/categorical columns, "
        f"and {date_count} likely date columns. "
        f"Key columns include: {key_columns}. "
        f"Current quality signals show {issues['missing_ratio']:.1%} missing values, "
        f"{issues['duplicate_ratio']:.1%} duplicates, and an estimated {issues['outlier_ratio']:.1%} outlier ratio."
    )


def build_suggested_questions(df, issues, profile, language="en"):
    numeric_cols = profile["numeric_columns"][:3]
    categorical_cols = profile["categorical_columns"][:3]
    top_cols = profile["top_columns"][:4]
    joined_top = ", ".join(top_cols) if top_cols else "the main columns"
    joined_num = ", ".join(numeric_cols) if numeric_cols else None
    joined_cat = ", ".join(categorical_cols) if categorical_cols else None

    if language == "ar":
        questions = [
            "ما أهم مشاكل جودة البيانات في هذا الملف؟",
            "هل الملف مناسب للتحليل أو التقارير؟ ولماذا؟",
            f"لخّص لي محتوى الملف وما الذي تمثله الأعمدة التالية: {joined_top}",
            "ما الأعمدة التي تحتاج تنظيفًا قبل استخدام البيانات؟",
            "هل توجد قيم مفقودة أو تكرارات أو أعمدة ثابتة يجب الانتباه لها؟",
        ]
        if joined_num:
            questions.append(f"حلّل الأعمدة الرقمية التالية وحدد أي قيم شاذة فيها: {joined_num}")
        if joined_cat:
            questions.append(f"ما أبرز الأنماط أو الفئات المتكررة في الأعمدة التالية: {joined_cat}؟")
        return questions

    questions = [
        "What are the main data quality issues in this file?",
        "Is this dataset ready for reporting or analysis, and why?",
        f"Summarize this file and explain what these columns likely represent: {joined_top}",
        "Which columns need cleaning before using this dataset?",
        "Are there missing values, duplicates, or constant columns that I should fix first?",
    ]
    if joined_num:
        questions.append(f"Analyze these numeric columns and identify possible outliers: {joined_num}")
    if joined_cat:
        questions.append(f"What are the main patterns or repeated categories in these columns: {joined_cat}?")
    return questions


def render_metric_cards(score, df, issues, ui):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(ui["score_label"], score)
    c2.metric(ui["rows"], df.shape[0])
    c3.metric(ui["columns"], df.shape[1])
    c4.metric(ui["missing_ratio"], f"{issues['missing_ratio']:.1%}")


st.set_page_config(page_title="AI Data Quality Analyst", layout="wide")
init_session_state()

current_language = st.session_state.get("ui_language", "ar")
ui = get_ui_labels(current_language)

st.title(ui["title"])
st.caption(ui["subtitle"])

if not os.getenv("OPENAI_API_KEY"):
    st.error(ui["api_key_missing"])
    st.stop()

with st.sidebar:
    language_label = st.selectbox(
        ui["language"],
        list(ui["language_options"].keys()),
        key="ui_language_select",
    )
    st.session_state["ui_language"] = ui["language_options"][language_label]
    current_language = st.session_state["ui_language"]
    ui = get_ui_labels(current_language)

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
    st.session_state["file_summary_result"] = None
    st.session_state["file_profile"] = None

uploaded = get_uploaded_file_from_session()

question = st.text_input(
    ui["question_label"],
    key="question_input",
    placeholder=ui["question_placeholder"],
)
st.caption(ui["ask_ai_hint"])

if uploaded is not None:
    st.success(ui["file_ready"])

    sheet_count = 1
    selected_sheet = None

    if uploaded.name.lower().endswith(".xlsx"):
        sheet_source = BytesIO(st.session_state["uploaded_file_bytes"])
        sheet_source.name = st.session_state["uploaded_file_name"]
        sheets = list_excel_sheets(sheet_source)
        sheet_count = len(sheets)

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
    file_profile = build_file_profile(
        df,
        st.session_state["uploaded_file_name"],
        selected_sheet=selected_sheet,
        sheet_count=sheet_count,
    )
    st.session_state["file_profile"] = file_profile

    render_metric_cards(score, df, issues, ui)

    top_left, top_right = st.columns([1.3, 1])
    with top_left:
        st.subheader(ui["preview_title"])
        st.dataframe(df.head(10), use_container_width=True)
    with top_right:
        st.subheader(ui["profile_title"])
        st.write(f"**{ui['file_name']}:** {file_profile['file_name']}")
        st.write(f"**{ui['file_type']}:** {file_profile['file_type']}")
        st.write(f"**{ui['sheet_count']}:** {file_profile['sheet_count'] if file_profile['sheet_count'] > 1 else ui['no_sheet']}")
        if file_profile.get("selected_sheet"):
            st.write(f"**{ui['sheet_label']}:** {file_profile['selected_sheet']}")
        st.write(f"**{ui['numeric_columns']}:** {len(file_profile['numeric_columns'])}")
        st.write(f"**{ui['categorical_columns']}:** {len(file_profile['categorical_columns'])}")
        st.write(f"**{ui['date_columns']}:** {len(file_profile['date_columns'])}")

    tabs = st.tabs([ui["summary_tab"], ui["suggestions_tab"], ui["charts_tab"], ui["data_tab"]])

    with tabs[0]:
        st.subheader(ui["file_summary_title"])
        summary_text = generate_file_summary_text(file_profile, issues, current_language)
        st.info(summary_text)

        if st.button(ui["auto_summary_button"], use_container_width=True):
            summary_question = (
                "لخص لي هذا الملف واشرح ماذا يحتوي، وما أهم الأعمدة، وما أهم مشاكل الجودة الحالية."
                if current_language == "ar"
                else "Summarize this file, explain what it contains, highlight the main columns, and describe the current key quality issues."
            )
            context = summarize_context(df, issues, outliers, file_profile)
            summary_result = ask_gpt(summary_question, context, analysis_type="general", language=current_language)
            st.session_state["file_summary_result"] = summary_result

        if st.session_state.get("file_summary_result") is not None:
            summary_result = st.session_state["file_summary_result"]
            st.markdown(f"### {ui['executive_summary']}")
            st.write(summary_result.get("executive_summary", ""))
            st.markdown(f"### {ui['direct_answer']}")
            st.write(summary_result.get("direct_answer", ""))

        st.markdown(f"### {ui['top_columns']}")
        st.write(", ".join(file_profile["top_columns"]) if file_profile["top_columns"] else "-")
        st.markdown(f"### {ui['sample_values']}")
        st.json(file_profile["sample_values"])

    with tabs[1]:
        st.subheader(ui["suggested_questions"])
        suggested_questions = build_suggested_questions(df, issues, file_profile, current_language)
        for idx, suggested_question in enumerate(suggested_questions):
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
        st.dataframe(df, use_container_width=True)

    if st.button(ui["analyze_button"], use_container_width=True, key="analyze_button"):
        if not question.strip():
            st.warning(ui["no_question_warning"])
        else:
            context = summarize_context(df, issues, outliers, file_profile)
            result = ask_gpt(question, context, analysis_type, language=current_language)

            st.session_state["history"].append((question, result))
            st.session_state["history"] = st.session_state["history"][-5:]
            st.session_state["latest_result"] = result
            st.session_state["latest_outliers"] = outliers
            st.session_state["latest_df"] = df
            st.session_state["latest_issues"] = issues

if st.session_state.get("latest_result") is not None:
    result = st.session_state["latest_result"]
    ui = get_ui_labels(st.session_state.get("ui_language", "ar"))
    outliers = st.session_state["latest_outliers"]
    df = st.session_state["latest_df"]
    issues = st.session_state["latest_issues"]

    st.success(ui["analysis_ready"])
    st.subheader(ui["executive_summary"])
    st.write(result.get("executive_summary", ""))

    st.subheader(ui["direct_answer"])
    st.write(result.get("direct_answer", ""))

    tab1, tab2, tab3 = st.tabs([ui["issues_tab"], ui["charts_tab"], ui["data_tab"]])

    with tab1:
        st.subheader(ui["findings"])
        findings = result.get("findings", [])
        for item in findings:
            st.write(f"- {item}")

        st.subheader(ui["recommendations"])
        recommendations = result.get("recommendations", [])
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
        st.pyplot(missing_chart(df, language=st.session_state.get("ui_language", "ar")))
        st.pyplot(outlier_chart(outliers, language=st.session_state.get("ui_language", "ar")))

    with tab3:
        st.dataframe(df, use_container_width=True)

    pdf = generate_pdf(result)
    st.download_button(
        ui["download_pdf"],
        pdf,
        file_name="report.pdf",
        mime="application/pdf",
        key="download_pdf_button",
    )

with st.sidebar:
    ui = get_ui_labels(st.session_state.get("ui_language", "ar"))
    st.subheader(ui["history_title"])
    for q, _ in st.session_state["history"][-5:]:
        st.write(f"- {q}")
