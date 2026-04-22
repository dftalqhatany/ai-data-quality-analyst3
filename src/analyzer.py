import pandas as pd
import numpy as np


def detect_outliers(df):

    numeric = df.select_dtypes(include=np.number)

    outlier_counts = {}

    for col in numeric.columns:
        q1 = numeric[col].quantile(0.25)
        q3 = numeric[col].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = numeric[(numeric[col] < lower) | (numeric[col] > upper)]

        outlier_counts[col] = len(outliers)

    return outlier_counts


def assess_readiness(df):

    rows, cols = df.shape

    missing_ratio = df.isna().sum().sum() / (rows * cols)

    duplicates_ratio = df.duplicated().sum() / rows

    empty_columns = df.columns[df.isna().all()].tolist()

    constant_columns = [
        col for col in df.columns if df[col].nunique() <= 1
    ]

    numeric = df.select_dtypes(include=np.number)

    outlier_total = 0

    for col in numeric.columns:
        q1 = numeric[col].quantile(0.25)
        q3 = numeric[col].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = numeric[(numeric[col] < lower) | (numeric[col] > upper)]

        outlier_total += len(outliers)

    outlier_ratio = outlier_total / rows if rows else 0

    score = 100

    score -= missing_ratio * 40
    score -= duplicates_ratio * 30
    score -= outlier_ratio * 20
    score -= len(empty_columns) * 2
    score -= len(constant_columns) * 2

    score = max(0, round(score, 2))

    issues = {
        "missing_ratio": missing_ratio,
        "duplicate_ratio": duplicates_ratio,
        "outlier_ratio": outlier_ratio,
        "empty_columns": empty_columns,
        "constant_columns": constant_columns
    }

    return score, issues
