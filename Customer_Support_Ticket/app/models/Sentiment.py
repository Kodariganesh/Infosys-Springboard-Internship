"""
Sentiment analysis wrapper (Sentiment.py)
"""
from app.sentiment.analyzer import HuggingFaceSentimentAnalyzer

# Keep one analyzer per process so the Hugging Face model is not reloaded for
# every API or dashboard request.
_analyzer = HuggingFaceSentimentAnalyzer()

def analyze_sentiment(subject: str, body: str):
    text = f"{subject} {body}".strip()
    result = _analyzer.analyze(text)
    # Map lowercase sentiment to Title Case or expected formats
    sent_map = {
        "positive": "Slightly Positive",
        "negative": "Slightly Negative",
        "neutral": "Neutral"
    }
    mapped_sent = sent_map.get(result.get("sentiment", "neutral"), "Neutral")
    
    # Return expected dict structure
    return {
        "sentiment": mapped_sent,
        "score": result.get("score", 0.5)
    }

def get_sentiment(title: str, body: str):
    return analyze_sentiment(title, body)
