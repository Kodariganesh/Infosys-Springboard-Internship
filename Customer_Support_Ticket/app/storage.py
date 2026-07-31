"""SQLite-backed local persistence for processed customer-support tickets."""

import sqlite3
from datetime import datetime, timezone

from app import config

DB_PATH = config.DATA_DIR / "tickets.db"


def _connect():
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with _connect() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_email TEXT, title TEXT NOT NULL, body TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 1, timestamp TEXT NOT NULL,
                sentiment TEXT NOT NULL, escalation TEXT, response TEXT NOT NULL DEFAULT ''
            )
        """)
        # Normalize values written by older JSON/SQLite implementations so the
        # dashboard only counts tickets with a real escalation reason.
        connection.execute("""
            UPDATE tickets
            SET escalation = NULL
            WHERE escalation = 0 OR escalation = 'No escalation triggered'
        """)


def save_ticket(title, body, sentiment, escalation, response="", customer_email=None, priority=1):
    """Save one processed ticket and return it as a dictionary."""
    initialize_database()
    escalation = escalation or None
    timestamp = datetime.now(timezone.utc).isoformat()
    with _connect() as connection:
        cursor = connection.execute("""
            INSERT INTO tickets
            (customer_email, title, body, priority, timestamp, sentiment, escalation, response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (customer_email, title, body, int(priority), timestamp, sentiment, escalation, response))
        ticket_id = cursor.lastrowid
    return {"id": ticket_id, "customer_email": customer_email, "title": title, "body": body,
            "priority": int(priority), "timestamp": timestamp, "sentiment": sentiment,
            "escalation": escalation, "response": response}


def load_tickets(limit=None):
    """Return saved tickets, newest first."""
    initialize_database()
    query, parameters = "SELECT * FROM tickets ORDER BY id DESC", ()
    if limit is not None:
        query, parameters = query + " LIMIT ?", (int(limit),)
    with _connect() as connection:
        return [dict(row) for row in connection.execute(query, parameters).fetchall()]
