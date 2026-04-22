# AI Data Quality Analyst 📊

AI Data Quality Analyst is an intelligent tool that analyzes datasets and evaluates their quality before using them in reporting, analysis, or machine learning tasks.

The application automatically scans the dataset, detects common data issues, and provides a **readiness score (0–100)** along with **clear recommendations and visual insights** to help improve the data before using it.

---

# Overview

Data often appears clean at first glance but may contain hidden problems such as:

- Missing values
- Duplicate records
- Inconsistent data types
- Outliers
- Poor column structure

These issues can cause incorrect results in reports, analytics, or machine learning models.

This project helps solve that problem by providing an **automated data quality assessment system** that evaluates datasets and generates useful insights.

---

# Key Features

### 1. Data Quality Analysis
The system automatically analyzes datasets and detects:

- Missing values
- Duplicate rows
- Outliers
- Data type inconsistencies
- Dataset structure issues

---

### 2. Readiness Scoring System
The application calculates a **Data Readiness Score (0–100)** that indicates how suitable the dataset is for the selected task.

Tasks include:

- **Reporting**
- **Data Analysis**
- **Machine Learning**

Each task has different quality requirements.

---

### 3. Visual Data Insights
The system generates visual charts to help users quickly understand dataset issues:

- Missing values chart
- Data types distribution
- Outlier visualization

---

### 4. AI-Powered Analysis
The project integrates AI to generate:

- Dataset summaries
- Quality evaluation explanations
- Practical improvement suggestions

This helps users understand **why the dataset received its score**.

---

### 5. Interactive Dashboard
The application includes a simple dashboard that shows:

- Dataset overview
- Quality metrics
- Charts and statistics
- AI recommendations

---

### 6. PDF Report Generation
Users can export a **professional PDF report** containing:

- Dataset summary
- Quality score
- Key findings
- Visual charts
- AI recommendations

---

# Project Structure

```
AI-Data-Quality-Analystv2
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── fonts
│   └── Cairo-Regular.ttf
│
└── src
    ├── analyzer.py
    ├── agent.py
    ├── ai_assistant.py
    ├── charts.py
    ├── io_utils.py
    └── pdf_report.py
```

### Main Components

**app.py**

Main application file that runs the interface and connects all modules.

**src/analyzer.py**

Handles dataset quality analysis including:

- Outlier detection
- Quality scoring
- Readiness evaluation

**src/agent.py**

Processes user input and prepares context for AI analysis.

**src/ai_assistant.py**

Handles communication with the AI model.

**src/io_utils.py**

Manages file reading and dataset loading.

**src/charts.py**

Creates visual charts for dataset insights.

**src/pdf_report.py**

Generates the final PDF report.

---

# Technologies Used

The project uses several tools and libraries:

- **Python**
- **Streamlit** – interactive web interface
- **Pandas** – data analysis
- **Matplotlib** – charts and visualizations
- **OpenAI API** – AI-generated insights
- **ReportLab** – PDF report generation
- **OpenPyXL** – Excel file support

---

# Installation

### 1. Clone the Repository

```bash
git clone https://github.com/dftalqhatany/AI-Data-Quality-Analystv2.git
cd AI-Data-Quality-Analystv2
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

Windows:

```bash
venv\Scripts\activate
```

Mac / Linux:

```bash
source venv/bin/activate
```

---

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

### 4. Set OpenAI API Key

Windows (PowerShell)

```bash
$env:OPENAI_API_KEY="your_api_key"
```

Mac / Linux

```bash
export OPENAI_API_KEY="your_api_key"
```

---

### 5. Run the Application

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

---

# How to Use

1. Upload a dataset (CSV or Excel).
2. Select the analysis goal (Reporting, Analysis, or Machine Learning).
3. Let the system analyze the dataset.
4. View the generated insights and charts.
5. Download the final PDF report if needed.

---

# Example Use Cases

This tool can help with:

- Preparing datasets for machine learning
- Checking data quality before analytics projects
- Evaluating datasets for dashboards or reports
- Understanding dataset issues quickly

---

# Future Improvements

Possible future features include:

- Database integration
- Automated data cleaning suggestions
- Advanced anomaly detection
- Multiple dataset comparison

---

# License

This project is released under the **MIT License**.

---

# Author

by:**Dalal & Hajer**

---

# Summary

AI Data Quality Analyst provides a simple way to answer an important question:

**"Is my dataset ready to be used?"**

By combining **data quality checks, AI insights, visual analysis, and reporting**, the tool helps users quickly understand their data and improve it before starting analysis or model development.
