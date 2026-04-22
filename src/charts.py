import matplotlib.pyplot as plt
import pandas as pd

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except Exception:
    arabic_reshaper = None
    get_display = None


def format_chart_text(text: str, language: str = "en") -> str:
    if not text:
        return ""

    if language != "ar":
        return text

    if arabic_reshaper and get_display:
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text

    return text


def set_chart_font():
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False


def missing_chart(df: pd.DataFrame, language: str = "en"):
    set_chart_font()

    missing_counts = df.isnull().sum()
    missing_counts = missing_counts[missing_counts > 0]

    fig, ax = plt.subplots(figsize=(10, 5))

    if missing_counts.empty:
        title = "No Missing Values" if language == "en" else "لا توجد قيم مفقودة"
        ax.set_title(format_chart_text(title, language), fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

    labels = [format_chart_text(str(col), language) for col in missing_counts.index.tolist()]
    ax.bar(labels, missing_counts.values)

    title = "Missing Values by Column" if language == "en" else "القيم المفقودة لكل عمود"
    ylabel = "Count" if language == "en" else "العدد"

    ax.set_title(format_chart_text(title, language), fontsize=14)
    ax.set_ylabel(format_chart_text(ylabel, language), fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    return fig


def outlier_chart(outliers: dict, language: str = "en"):
    set_chart_font()

    fig, ax = plt.subplots(figsize=(10, 5))

    if not outliers:
        title = "No Outliers Detected" if language == "en" else "لا توجد قيم شاذة"
        ax.set_title(format_chart_text(title, language), fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

    labels = [format_chart_text(str(col), language) for col in outliers.keys()]
    values = list(outliers.values())

    ax.bar(labels, values)

    title = "Outliers by Column" if language == "en" else "القيم الشاذة لكل عمود"
    ylabel = "Count" if language == "en" else "العدد"

    ax.set_title(format_chart_text(title, language), fontsize=14)
    ax.set_ylabel(format_chart_text(ylabel, language), fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    return fig
