"""
Tests for the application modules
"""

import unittest
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


if __name__ == '__main__':
    unittest.main()
