"""
Sentiment analysis using HuggingFace models or Grok API
"""

import requests
import json
import logging
from app import config

logger = logging.getLogger(__name__)


class HuggingFaceSentimentAnalyzer:
    """Analyze sentiment using Hugging Face pipelines"""
    
    def __init__(self):
        self.pipeline = None
        # Lazy load pipeline to avoid loading heavy models unnecessarily
        
    def _load_pipeline(self):
        if self.pipeline is None:
            try:
                from transformers import pipeline
                # Use HF Token if provided
                use_auth_token = config.HF_TOKEN if config.HF_TOKEN else None
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model=config.SENTIMENT_MODEL,
                    token=use_auth_token
                )
            except Exception as e:
                logger.error(f"Failed to load Hugging Face pipeline: {e}")
                raise e

    def analyze(self, text):
        """
        Analyze sentiment of the given text
        
        Args:
            text: String to analyze
            
        Returns:
            Dict with 'sentiment' (positive/negative/neutral) and 'score' (float)
        """
        if not text or not isinstance(text, str) or len(text.strip()) == 0:
            return {"sentiment": "neutral", "score": 0.0}
            
        try:
            self._load_pipeline()
            result = self.pipeline(text)[0]
            label = result['label'].lower()
            score = result['score']
            
            # Map standard model outputs if necessary
            if label in ['positive', 'negative']:
                sentiment = label
            elif 'star' in label or 'label' in label:
                # Some models return "5 stars" or "LABEL_1"
                sentiment = "positive" if "star" in label and ("4" in label or "5" in label) else "negative"
            else:
                sentiment = "positive" if label == "pos" else "negative" if label == "neg" else "neutral"
                
            return {
                "sentiment": sentiment,
                "score": score
            }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {"sentiment": "neutral", "score": 0.0}


class GrokSentimentAnalyzer:
    """Analyze sentiment using the Grok API"""
    
    def __init__(self):
        self.api_key = config.GROK_API_KEY
        self.api_url = config.GROK_API_URL

    def analyze(self, text):
        """
        Analyze sentiment of text using Grok API
        """
        if not self.api_key:
            logger.warning("Grok API key is not configured. Falling back to default.")
            return {"sentiment": "neutral", "score": 0.0}
            
        if not text or not isinstance(text, str) or len(text.strip()) == 0:
            return {"sentiment": "neutral", "score": 0.0}
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "grok-2-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a sentiment analysis assistant. Analyze the sentiment of the text. Respond ONLY with a JSON object in this format: {\"sentiment\": \"positive\"/\"negative\"/\"neutral\", \"score\": float between 0.0 and 1.0}"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.0
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            response_data = response.json()
            content = response_data['choices'][0]['message']['content'].strip()
            
            # Extract JSON from response
            try:
                result = json.loads(content)
                return {
                    "sentiment": result.get("sentiment", "neutral").lower(),
                    "score": float(result.get("score", 0.0))
                }
            except json.JSONDecodeError:
                # Fallback simple search
                if "positive" in content.lower():
                    return {"sentiment": "positive", "score": 0.8}
                elif "negative" in content.lower():
                    return {"sentiment": "negative", "score": 0.8}
                return {"sentiment": "neutral", "score": 0.5}
                
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            return {"sentiment": "neutral", "score": 0.0}
