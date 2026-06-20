"""
Configuration settings for the Customer Support Ticket system
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
APP_DIR = PROJECT_ROOT / "app"
MODELS_DIR = APP_DIR / "models"

# Create directories if they don't exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Data file paths
DATA_CSV_PATH = DATA_DIR / "customer_support_tickets.csv"

# API Configuration
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Sentiment Analysis Configuration
HF_TOKEN = os.getenv("HF_TOKEN", "")
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

# Escalation Configuration
HIGH_PRIORITY_THRESHOLD = 3
ESCALATION_KEYWORDS = ["critical", "urgent", "severe", "major"]

# Model Configuration
RESPONSE_PREDICTION_MODEL = MODELS_DIR / "response_model.pkl"
SENTIMENT_ANALYSIS_MODEL = MODELS_DIR / "sentiment_model.pkl"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
