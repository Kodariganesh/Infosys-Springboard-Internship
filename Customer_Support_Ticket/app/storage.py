"""SQLite-backed local persistence for processed customer-support tickets."""

import sqlite3
from datetime import datetime, timezone

from app import config

DB_PATH = config.DATA_DIR / "tickets.db"


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = _connect()
    try:
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
        connection.commit()
    finally:
        connection.close()


def save_ticket(title, body, sentiment, escalation, response="", customer_email=None, priority=1):
    """Save one processed ticket and return it as a dictionary."""
    initialize_database()
    escalation = escalation or None
    timestamp = datetime.now(timezone.utc).isoformat()
    connection = _connect()
    try:
        cursor = connection.execute("""
            INSERT INTO tickets
            (customer_email, title, body, priority, timestamp, sentiment, escalation, response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (customer_email, title, body, int(priority), timestamp, sentiment, escalation, response))
        ticket_id = cursor.lastrowid
        connection.commit()
    finally:
        connection.close()
    return {"id": ticket_id, "customer_email": customer_email, "title": title, "body": body,
            "priority": int(priority), "timestamp": timestamp, "sentiment": sentiment,
            "escalation": escalation, "response": response}


def load_tickets(limit=None):
    """Return saved tickets, newest first."""
    initialize_database()
    query, parameters = "SELECT * FROM tickets ORDER BY id DESC", ()
    if limit is not None:
        query, parameters = query + " LIMIT ?", (int(limit),)
    connection = _connect()
    try:
        return [dict(row) for row in connection.execute(query, parameters).fetchall()]
    finally:
        connection.close()
