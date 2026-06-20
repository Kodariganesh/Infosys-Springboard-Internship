"""
Ticket escalation logic based on priority levels and keywords
"""

import logging
from app import config

logger = logging.getLogger(__name__)


class TicketEscalator:
    """Escalation evaluator for customer support tickets"""
    
    def __init__(self):
        self.priority_threshold = config.HIGH_PRIORITY_THRESHOLD
        self.keywords = config.ESCALATION_KEYWORDS

    def should_escalate(self, priority, text=""):
        """
        Evaluate if a ticket should be escalated
        
        Args:
            priority: Numeric priority level
            text: Text content (subject + body) to check for keywords
            
        Returns:
            Tuple (bool, str) showing if it should escalate and the reason
        """
        # Priority escalation
        try:
            p_val = int(priority)
            if p_val >= self.priority_threshold:
                return True, f"High Priority Level ({p_val})"
        except (ValueError, TypeError):
            pass
            
        # Keyword-based escalation
        if text and isinstance(text, str):
            text_lower = text.lower()
            for kw in self.keywords:
                if kw in text_lower:
                    return True, f"Escalation Keyword Found: '{kw}'"
                    
        return False, "No escalation triggered"

    def escalate_tickets(self, df):
        """
        Process a batch of tickets and add escalation status columns
        
        Args:
            df: pandas DataFrame
            
        Returns:
            DataFrame with 'escalated' (bool) and 'escalation_reason' (str) columns
        """
        logger.info(f"Processing {len(df)} tickets for escalation evaluation.")
        df = df.copy()
        
        escalated_list = []
        reason_list = []
        
        # Determine column names based on dataset format
        subject_col = 'Ticket Subject' if 'Ticket Subject' in df.columns else 'subject'
        body_col = 'Ticket Description' if 'Ticket Description' in df.columns else 'body'
        priority_col = 'Ticket Priority' if 'Ticket Priority' in df.columns else 'priority'
        
        for idx, row in df.iterrows():
            subject = str(row.get(subject_col, ''))
            body = str(row.get(body_col, ''))
            priority = row.get(priority_col, 1)
            
            should_esc, reason = self.should_escalate(priority, f"{subject} {body}")
            
            escalated_list.append(should_esc)
            reason_list.append(reason)
            
        df['escalated'] = escalated_list
        df['escalation_reason'] = reason_list
        
        num_escalated = sum(escalated_list)
        logger.info(f"Escalation process complete: {num_escalated}/{len(df)} tickets escalated.")
        
        return df
