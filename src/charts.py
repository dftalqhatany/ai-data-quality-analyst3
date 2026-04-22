import matplotlib.pyplot as plt
from matplotlib import font_manager


def detect_language(text: str) -> str:
    if not text:
        return "en"

    arabic_chars = sum(1 for ch in text if "\u0600" <= ch <= "\u06FF")
    english_chars = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))

    if arabic_chars > english_chars:
        return "ar"
    return "en"


def configure_chart_font(language="en"):
    if language != "ar":
        return

    preferred_fonts = [
        "Cairo",
        "Noto Naskh Arabic",
        "Amiri",
        "Arial",
        "Tahoma",
        "DejaVu Sans",
    ]

    available = {f.name for f in font_manager.fontManager.ttflist}

    for font_name in preferred_fonts:
        if font_name in available:
            plt.rcParams["font.family"] = font_name
            break

    plt.rcParams["axes.unicode_minus"] = False


def get_chart_labels(language="en"):
    if language == "ar":
        return {
            "missing_title": "القيم المفقودة لكل عمود",
            "outlier_title": "القيم الشاذة لكل عمود",
            "x_label": "الأعمدة",
            "y_label": "العدد",
        }

    return {
        "missing_title": "Missing Values per Column",
        "outlier_title": "Outliers per Column",
        "x_label": "Columns",
        "y_label": "Count",
    }


def missing_chart(df, language="en"):
    configure_chart_font(language)
    labels = get_chart_labels(language)

    missing = df.isna().sum()

    fig, ax = plt.subplots()
    missing.plot(kind="bar", ax=ax)

    ax.set_title(labels["missing_title"])
    ax.set_xlabel(labels["x_label"])
    ax.set_ylabel(labels["y_label"])

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig


def outlier_chart(outliers, language="en"):
    configure_chart_font(language)
    labels = get_chart_labels(language)

    fig, ax = plt.subplots()

    cols = list(outliers.keys())
    values = list(outliers.values())

    ax.bar(cols, values)

    ax.set_title(labels["outlier_title"])
    ax.set_xlabel(labels["x_label"])
    ax.set_ylabel(labels["y_label"])

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig
