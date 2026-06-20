from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import json
import datetime
from pathlib import Path

import sys
from pathlib import Path

# Add project root to Python path to ensure 'app' imports work correctly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import wrappers
from app.models.Sentiment import get_sentiment
from app.models.Response import automate_response
from app.models.Issue import escalateit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Core Support API Server",
    description="Backend API processing ticket sentiment, escalation, and auto-replies.",
    version="1.0.0"
)

# Central configuration paths for saving processed tickets locally
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TICKETS_DB_PATH = DATA_DIR / "local_tickets_db.json"


# Define the Ticket schema
class Ticket(BaseModel):
    subject: str
    body: str
    customer_email: str


# Define the response schema
class TicketProcessedResponse(BaseModel):
    subject: str
    body: str
    customer_email: str
    sentiment: str
    sentiment_score: float
    escalation_status: str
    auto_response: str
    saved_to_db: bool


# Function to save ticket locally for consistency with Streamlit UI
def save_ticket_locally(email, title, body, sentiment, escalation, response):
    tickets = []
    if TICKETS_DB_PATH.exists():
        try:
            with open(TICKETS_DB_PATH, "r") as f:
                tickets = json.load(f)
        except Exception:
            tickets = []

    new_ticket = {
        "id": len(tickets) + 1,
        "email": email,
        "title": title,
        "body": body,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "sentiment": sentiment,
        "escalation": escalation,
        "response": response,
    }
    tickets.append(new_ticket)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(TICKETS_DB_PATH, "w") as f:
            json.dump(tickets, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Failed to save ticket locally: {e}")
        return False


@app.post("/process-ticket/", response_model=TicketProcessedResponse)
async def process_ticket(ticket: Ticket):
    try:
        # Step 1: Run Sentiment Analysis
        sentiment_res = get_sentiment(ticket.subject, ticket.body)
        sentiment = sentiment_res.get("sentiment", "Neutral")
        score = sentiment_res.get("score", 0.5)

        # Step 2: Evaluate Escalation Status
        escalated_reason = escalateit(ticket.subject, ticket.body)
        escalation_status = escalated_reason if escalated_reason else "No escalation triggered"

        # Step 3: Draft Template Response
        reply_subject, reply_body = automate_response(
            ticket.subject, ticket.body
        )
        combined_response = f"{reply_subject}\n\n{reply_body}"

        # Step 4: Persist locally
        saved_local = save_ticket_locally(
            ticket.customer_email,
            ticket.subject,
            ticket.body,
            sentiment,
            escalation_status,
            combined_response,
        )

        return TicketProcessedResponse(
            subject=ticket.subject,
            body=ticket.body,
            customer_email=ticket.customer_email,
            sentiment=sentiment,
            sentiment_score=score,
            escalation_status=escalation_status,
            auto_response=combined_response,
            saved_to_db=saved_local,
        )
    except Exception as e:
        logger.error(f"API Error processing ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    return {"status": "online", "storage_mode": "local_json"}
