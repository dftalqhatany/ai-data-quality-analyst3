import pandas as pd


def load_dataframe(uploaded_file, sheet_name=None):
    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        encodings = ["utf-8", "utf-8-sig", "latin1"]
        for enc in encodings:
            try:
                uploaded_file.seek(0)
                return pd.read_csv(uploaded_file, encoding=enc)
            except Exception:
                continue
        raise ValueError("Could not read CSV file with supported encodings.")

    if name.endswith(".xlsx"):
        uploaded_file.seek(0)
        if sheet_name:
            return pd.read_excel(uploaded_file, sheet_name=sheet_name, engine="openpyxl")
        return pd.read_excel(uploaded_file, engine="openpyxl")

    raise ValueError("Unsupported file type")


def list_excel_sheets(uploaded_file):
    uploaded_file.seek(0)
    xls = pd.ExcelFile(uploaded_file, engine="openpyxl")
    return xls.sheet_names
