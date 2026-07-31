from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
from pathlib import Path

import sys

# Add project root to Python path to ensure 'app' imports work correctly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import wrappers
from app.models.Sentiment import get_sentiment
from app.models.Response import automate_response
from app.models.Issue import escalateit
from app.storage import save_ticket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Core Support API Server",
    description="Backend API processing ticket sentiment, escalation, and auto-replies.",
    version="1.0.0"
)

# Define the Ticket schema
class Ticket(BaseModel):
    subject: str
    body: str
    customer_email: str
    priority: int = Field(default=1, ge=1, le=5)


# Define the response schema
class TicketProcessedResponse(BaseModel):
    subject: str
    body: str
    customer_email: str
    priority: int
    sentiment: str
    sentiment_score: float
    escalation_status: str
    auto_response: str
    saved_to_db: bool


@app.post("/process-ticket/", response_model=TicketProcessedResponse)
def process_ticket(ticket: Ticket):
    try:
        # Step 1: Run Sentiment Analysis
        sentiment_res = get_sentiment(ticket.subject, ticket.body)
        sentiment = sentiment_res.get("sentiment", "Neutral")
        score = sentiment_res.get("score", 0.5)

        # Step 2: Evaluate Escalation Status
        escalated_reason = escalateit(ticket.subject, ticket.body, ticket.priority)
        escalation_status = escalated_reason if escalated_reason else "No escalation triggered"

        # Step 3: Draft Template Response
        reply_subject, reply_body = automate_response(
            ticket.subject, ticket.body, sentiment=sentiment
        )
        combined_response = f"{reply_subject}\n\n{reply_body}"

        # Step 4: Persist locally
        save_ticket(ticket.subject, ticket.body, sentiment, escalated_reason, combined_response,
                    customer_email=ticket.customer_email, priority=ticket.priority)

        return TicketProcessedResponse(
            subject=ticket.subject,
            body=ticket.body,
            customer_email=ticket.customer_email,
            priority=ticket.priority,
            sentiment=sentiment,
            sentiment_score=score,
            escalation_status=escalation_status,
            auto_response=combined_response,
            saved_to_db=True,
        )
    except Exception as e:
        logger.error(f"API Error processing ticket: {e}")
        raise HTTPException(status_code=500, detail="Ticket processing failed. Please try again later.")


@app.get("/")
def read_root():
    return {"status": "online", "storage_mode": "sqlite"}
