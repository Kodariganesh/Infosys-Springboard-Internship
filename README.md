# Customer Support Ticket Automation System

## Overview

The **Customer Support Ticket Automation System** is an AI-assisted support workflow built for the Infosys Springboard Internship. It helps process customer support tickets by analyzing customer sentiment, identifying tickets that require escalation, generating draft replies, and storing processed ticket activity for dashboard reporting.

The current implementation is a Python application with a Streamlit dashboard, FastAPI backend, command-line pipeline, Hugging Face sentiment analysis, rule-based escalation, provider-backed response generation, and SQLite persistence.

---

## Features

1. **Sentiment Analysis**
   Uses a Hugging Face sentiment pipeline or a locally trained model to classify customer messages as positive, neutral, or negative.

2. **Real-Time Escalation**
   Escalates tickets when the priority is high or when full-word critical keywords are detected, such as `critical`, `urgent`, `severe`, or `major`.

3. **Automated Response Drafting**
   Generates support reply drafts using Gemini, Hugging Face, or Grok when API keys are configured. If no provider key is available, the system falls back to local response templates.

4. **Streamlit Dashboard**
   Provides pages for ticket metrics, sentiment analysis, escalation checking, and automated response generation.

5. **FastAPI Backend**
   Exposes an API endpoint for processing tickets programmatically.

6. **SQLite Storage**
   Stores processed tickets locally in `Customer_Support_Ticket/data/tickets.db`.

7. **CLI Pipeline**
   Supports dataset analysis, sentiment sampling, full-dataset escalation, and response generation from the command line.

---

## Current Scope

This repository currently implements the Python application under `Customer_Support_Ticket/`.

Earlier drafts of the project may mention Pinecone, Zapier, ngrok, Google Sheets, Slack, OpenAI GPT, vector databases, and notebook-based pipelines. Those integrations are **not present in the current codebase** and should be treated as future enhancements unless the missing files and modules are added.

---

## Project Flow

```text
Customer Ticket Input
        |
        v
Collect Subject, Body, Email, Priority
        |
        v
Run Sentiment Analysis
        |
        v
Check Escalation Rules
        |
        v
Generate Draft Support Response
        |
        v
Save Processed Ticket to SQLite
        |
        v
Display Metrics in Dashboard / Return API Response
```

---

## Directory Structure

```text
Infosys-Springboard-Internship/
|
|-- Customer_Support_Ticket/
|   |-- app/
|   |   |-- analysis/             # CSV loading and cleaning
|   |   |-- escalation/           # Priority and keyword escalation logic
|   |   |-- models/               # Wrapper functions used by API/dashboard
|   |   |-- responses/            # AI/template response generation
|   |   |-- sentiment/            # Hugging Face sentiment analyzer
|   |   |-- api.py                # FastAPI backend
|   |   |-- config.py             # Paths, API keys, and settings
|   |   |-- dashboard.py          # Streamlit dashboard
|   |   `-- training.py           # Optional local model training
|   |
|   |-- data/
|   |   `-- customer_support_tickets.csv
|   |
|   |-- main.py                   # CLI entry point
|   |-- requirements.txt          # Python dependencies
|   |-- test_app.py               # Unit tests
|   |-- quickstart.bat            # Windows setup helper
|   `-- quickstart.sh             # Linux/macOS setup helper
|
|-- Project Report Documentation/ # Agile, defect, and test-plan documents
|-- LICENSE
`-- README.md
```

---

## Setup

### 1. Create and Activate Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\activate.bat
```

If PowerShell blocks activation scripts, run commands directly through the virtual environment Python:

```powershell
.\venv\Scripts\python.exe -m pip install -r Customer_Support_Ticket\requirements.txt
```

### 2. Install Dependencies

```powershell
.\venv\Scripts\python.exe -m pip install -r Customer_Support_Ticket\requirements.txt
```

### 3. Configure Environment Variables

Copy the sample env file:

```powershell
copy Customer_Support_Ticket\.env.example Customer_Support_Ticket\.env
```

Then update `Customer_Support_Ticket/.env`:

```env
GEMINI_API_KEY=
HF_TOKEN=
GROK_API_KEY=
LOG_LEVEL=INFO
```

API keys are optional. Without them, the response generator uses local templates.

---

## Run the Application

### Streamlit Dashboard

```powershell
.\venv\Scripts\python.exe -m streamlit run Customer_Support_Ticket\app\dashboard.py
```

Open:

```text
http://localhost:8501
```

### FastAPI Backend

```powershell
.\venv\Scripts\python.exe -m uvicorn Customer_Support_Ticket.app.api:app --reload
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### CLI Pipeline

```powershell
.\venv\Scripts\python.exe Customer_Support_Ticket\main.py --action all --sample-size 10
```

Available actions:

```text
all
analyze
sentiment
escalate
respond
```

---

## API Example

Endpoint:

```text
POST /process-ticket/
```

Sample request:

```json
{
  "subject": "Critical payment failure",
  "body": "My payment failed multiple times and I need urgent help.",
  "customer_email": "customer@example.com",
  "priority": 4
}
```

Sample response fields:

```json
{
  "sentiment": "Slightly Negative",
  "sentiment_score": 0.98,
  "escalation_status": "High Priority Level (4)",
  "saved_to_db": true
}
```

---

## Testing

Run the unit tests:

```powershell
.\venv\Scripts\python.exe -m unittest Customer_Support_Ticket/test_app.py
```

Latest verified result:

```text
Ran 11 tests
OK
```

---

## Recent Fixes

- Fixed SQLite connection handling so temporary test databases are not locked on Windows.
- Improved escalation keyword matching to avoid false matches like `major` inside `majority`.
- Updated negative response templates so they do not claim a ticket was escalated unless escalation actually happened.
- Updated the CLI pipeline so escalation runs on the full cleaned dataset.
- Added empty dataset handling in the CSV cleaning logic.
- Cleaned dashboard text and README encoding issues.

---

## Future Enhancements

- Add Pinecone or another vector database for similar-ticket retrieval.
- Add email automation through Zapier or a direct email API.
- Add role-based admin views for support teams.
- Add richer analytics for recurring issue prevention.
- Add integration tests for the FastAPI endpoint.

---

## Conclusion

This project demonstrates an end-to-end customer support automation prototype with NLP, escalation rules, response drafting, API access, dashboard monitoring, and local persistence. It is suitable as a working internship project and can be extended with vector search and third-party integrations in a future version.
