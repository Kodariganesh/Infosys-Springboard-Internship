# Customer Support Tickets (Infosys Springboard Internship)

## Overview
The **Customer Support Ticket Automation & Prevention System** is a comprehensive software suite developed during the Infosys Springboard Internship. The project is designed to optimize customer support operations by utilizing Natural Language Processing (NLP) and Generative AI (Google Gemini) to analyze tickets, flag escalations, and draft automated replies in real-time.

---

## Key Features

1. **Modular Architecture**: Rebuilt from experimental drafts into clean, decoupled Python packages representing data loaders, sentiment analyzers, escalator modules, and auto-response generators.
2. **Sentiment Analysis**: Integrates a local Hugging Face NLP pipeline (`distilbert-base-uncased-sst-2`) to classify customer queries as Positive, Neutral, or Negative with confidence scoring.
3. **Real-Time Escalation**: Evaluates tickets in real-time against priority thresholds and critical keyword filters (e.g. *"critical"*, *"crashed"*) to flag urgent items.
4. **Free Generative AI Integrations**: Leverages a robust multi-LLM sequence for auto-drafting email replies:
   * **Google Gemini 2.5 Flash** (Free tier via Google AI Studio).
   * **Hugging Face Serverless Chat API** (Free backup).
   * **Grok 2 Mini** (Optional paid key).
   * **Local Templates** (Offline fail-safe).
5. **Interactive UI Dashboard**: Displays metrics cards, real-time ticket logs, data distributions, and interactive forms via Streamlit.
6. **REST API Interface**: Exposes a FastAPI application served by Uvicorn, complete with interactive Swagger documentation.

---

## Directory Structure

```text
Infosys-Springboard-Internship/
│
├── Customer_Support_Ticket/      # Core Application Codebase
│   ├── app/
│   │   ├── analysis/             # CSV data loader and cleaning logic
│   │   ├── escalation/           # Keyword and priority escalation checks
│   │   ├── models/               # Simple wrapper interfaces (Sentiment, Issue, Response)
│   │   ├── responses/            # AI reply generator (Gemini / HF / Grok)
│   │   ├── sentiment/            # Hugging Face NLP pipelines
│   │   │
│   │   ├── api.py                # FastAPI REST Server
│   │   ├── config.py             # Settings and environment loader
│   │   ├── dashboard.py          # Streamlit UI Dashboard
│   │   └── training.py           # Model training script
│   │
│   ├── data/                     # Data directory (CSV dataset, local JSON DB)
│   ├── logs/                     # Background application log folder
│   │
│   ├── main.py                   # Command Line runner
│   ├── test_app.py               # Application unit test suite
│   ├── requirements.txt          # Python packages list
│   ├── quickstart.bat            # Windows setup script
│   └── quickstart.sh             # Linux/macOS setup script
│
├── Project Report Documentation/ # Excel Sheets (Agile track, defect logs, test plan)
└── .gitignore                    # Git file exclusions (venv, logs, .env)
```

---

## Setup & Running Guide

### 1. Prerequisite Setup
Generate a free API key at **[Google AI Studio](https://aistudio.google.com/)**.

Open the project folder, create a file named `.env` inside `Customer_Support_Ticket/`, and populate it:
```env
# Google Gemini API key (Free Tier)
GEMINI_API_KEY="your_api_key_here"

# Optional Hugging Face Token (Free fallback)
HF_TOKEN=""

# Logging level (DEBUG, INFO, WARNING)
LOG_LEVEL=INFO
```

### 2. Start the Frontend Dashboard (Streamlit)
To launch the interactive visual dashboard:
```powershell
# Open terminal inside the workspace directory and run:
.\venv\Scripts\python.exe -m streamlit run Customer_Support_Ticket\app\dashboard.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

### 3. Start the Backend Server (FastAPI / Uvicorn)
To run the programmatic backend API:
```powershell
.\venv\Scripts\python.exe -m uvicorn Customer_Support_Ticket.app.api:app --reload
```
Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** to test the endpoints interactively.

---

## Testing & Validation
Verify that all packages are loading and executing correctly by running the unit test suite:
```powershell
.\venv\Scripts\python.exe -m unittest Customer_Support_Ticket/test_app.py
```

---

## Conclusion
The **Customer Support Tickets** system is a comprehensive, production-ready solution that bridges machine learning analysis with software interfaces. By utilizing modern web dashboards, REST APIs, and free GenAI integrations, this project demonstrates standard best practices in AI-integrated software engineering.
