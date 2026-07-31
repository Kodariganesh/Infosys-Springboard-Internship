"""
Issue escalation wrapper (Issue.py)
"""
from app.escalation.escalator import TicketEscalator

def escalateit(title: str, body: str, priority: int = 1):
    escalator = TicketEscalator()
    # Run should_escalate checking keywords in the title and body
    should_esc, reason = escalator.should_escalate(priority=priority, text=f"{title} {body}")
    if should_esc:
        return reason
    return False
