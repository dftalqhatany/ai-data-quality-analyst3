from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from bidi.algorithm import get_display
import arabic_reshaper
from datetime import datetime
import io
import os


def detect_language(text: str) -> str:
    if not text:
        return "en"

    arabic_chars = sum(1 for ch in text if "\u0600" <= ch <= "\u06FF")
    english_chars = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))

    if arabic_chars > english_chars:
        return "ar"
    return "en"


def shape_arabic_text(text):
    if text is None:
        return ""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)


def prepare_text(text, language="en"):
    text = "" if text is None else str(text)
    if language == "ar":
        return shape_arabic_text(text)
    return text


def register_fonts():
    font_path = os.path.join("fonts", "Cairo-Regular.ttf")
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("CairoArabic", font_path))
        return "CairoArabic"
    return "Helvetica"


def generate_pdf(result):
    language = result.get("_language", "en")
    font_name = register_fonts()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    if language == "ar":
        normal_style = ParagraphStyle(
            name="ArabicNormal",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=11,
            leading=16,
            alignment=TA_RIGHT,
        )
        heading_style = ParagraphStyle(
            name="ArabicHeading",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=14,
            leading=18,
            alignment=TA_RIGHT,
        )

        title = "تقرير جودة البيانات بالذكاء الاصطناعي"
        generated_at = f"تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        executive_summary_title = "الملخص التنفيذي"
        direct_answer_title = "الإجابة المباشرة"
        findings_title = "النتائج"
        recommendations_title = "التوصيات"
        next_steps_title = "الخطوات التالية"
    else:
        normal_style = ParagraphStyle(
            name="EnglishNormal",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=11,
            leading=16,
            alignment=TA_LEFT,
        )
        heading_style = ParagraphStyle(
            name="EnglishHeading",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=14,
            leading=18,
            alignment=TA_LEFT,
        )

        title = "AI Data Quality Report"
        generated_at = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        executive_summary_title = "Executive Summary"
        direct_answer_title = "Direct Answer"
        findings_title = "Findings"
        recommendations_title = "Recommendations"
        next_steps_title = "Next Steps"

    elements = []

    elements.append(Paragraph(prepare_text(title, language), heading_style))
    elements.append(Paragraph(prepare_text(generated_at, language), normal_style))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph(prepare_text(executive_summary_title, language), heading_style))
    elements.append(Paragraph(prepare_text(result.get("executive_summary", ""), language), normal_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(prepare_text(direct_answer_title, language), heading_style))
    elements.append(Paragraph(prepare_text(result.get("direct_answer", ""), language), normal_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(prepare_text(findings_title, language), heading_style))
    for item in result.get("findings", []):
        bullet = f"- {item}"
        elements.append(Paragraph(prepare_text(bullet, language), normal_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(prepare_text(recommendations_title, language), heading_style))
    for item in result.get("recommendations", []):
        bullet = f"- {item}"
        elements.append(Paragraph(prepare_text(bullet, language), normal_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(prepare_text(next_steps_title, language), heading_style))
    for item in result.get("next_steps", []):
        bullet = f"- {item}"
        elements.append(Paragraph(prepare_text(bullet, language), normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
