"""
Tests for the application modules
"""

import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


class TestConfig(unittest.TestCase):
    """Test configuration module"""
    
    def test_config_imports(self):
        """Test that config can be imported"""
        from app import config
        self.assertIsNotNone(config.DATA_DIR)
        self.assertIsNotNone(config.APP_DIR)


class TestDataLoader(unittest.TestCase):
    """Test data loading and preprocessing"""
    
    def test_data_loader_imports(self):
        """Test that data loader can be imported"""
        from app.analysis.data_loader import load_data, clean_data
        self.assertIsNotNone(load_data)
        self.assertIsNotNone(clean_data)


class TestSentimentAnalyzer(unittest.TestCase):
    """Test sentiment analysis module"""
    
    def test_sentiment_analyzer_imports(self):
        """Test that sentiment analyzer can be imported"""
        from app.sentiment.analyzer import HuggingFaceSentimentAnalyzer
        self.assertIsNotNone(HuggingFaceSentimentAnalyzer)


class TestEscalator(unittest.TestCase):
    """Test ticket escalation module"""
    
    def test_escalator_imports(self):
        """Test that escalator can be imported"""
        from app.escalation.escalator import TicketEscalator
        self.assertIsNotNone(TicketEscalator)
    
    def test_escalation_logic(self):
        """Test escalation logic"""
        from app.escalation.escalator import TicketEscalator
        escalator = TicketEscalator()
        
        # High priority should escalate
        self.assertTrue(escalator.should_escalate(priority=5)[0])
        
        # Low priority should not escalate
        self.assertFalse(escalator.should_escalate(priority=1)[0])

        # Critical keywords should escalate even at a low priority.
        self.assertTrue(escalator.should_escalate(priority=1, text="Critical outage")[0])


class TestStorage(unittest.TestCase):
    """Test SQLite ticket persistence without touching application data."""

    def test_ticket_round_trip(self):
        from app import storage
        original_db_path = storage.DB_PATH
        with tempfile.TemporaryDirectory() as temp_dir:
            storage.DB_PATH = Path(temp_dir) / "tickets.db"
            try:
                saved = storage.save_ticket("Billing issue", "Payment failed", "Slightly Negative",
                                            "High Priority Level (4)", priority=4)
                tickets = storage.load_tickets()
            finally:
                storage.DB_PATH = original_db_path

        self.assertEqual(saved["priority"], 4)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]["title"], "Billing issue")

    def test_false_escalation_is_stored_as_empty(self):
        from app import storage
        original_db_path = storage.DB_PATH
        with tempfile.TemporaryDirectory() as temp_dir:
            storage.DB_PATH = Path(temp_dir) / "tickets.db"
            try:
                storage.save_ticket("Question", "How do I update my profile?", "Neutral", False)
                ticket = storage.load_tickets()[0]
            finally:
                storage.DB_PATH = original_db_path

        self.assertIsNone(ticket["escalation"])


class TestResponseGenerator(unittest.TestCase):
    """Test response generation module"""
    
    def test_response_generator_imports(self):
        """Test that response generator can be imported"""
        from app.responses.generator import ResponseGenerator
        self.assertIsNotNone(ResponseGenerator)
    
    def test_response_generation(self):
        """Test response generation"""
        from app.responses.generator import ResponseGenerator
        generator = ResponseGenerator()
        
        response = generator.generate_response(
            "Test subject",
            "Test body",
            "positive"
        )
        
        self.assertIn('base_response', response)
        self.assertIn('keywords', response)
        self.assertIn('suggestions', response)

    def test_response_wrapper_reuses_provided_sentiment(self):
        """A caller-provided sentiment must avoid a second model inference."""
        from app.models.Response import automate_response
        with patch("app.models.Response.get_sentiment") as mock_sentiment:
            subject, body = automate_response("Test subject", "Test body", sentiment="positive")

        mock_sentiment.assert_not_called()
        self.assertEqual(subject, "Re: Test subject")
        self.assertTrue(body)


if __name__ == '__main__':
    unittest.main()
