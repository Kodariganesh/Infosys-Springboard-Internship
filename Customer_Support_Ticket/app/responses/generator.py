"""
Suggested customer support reply template generator
"""

import logging
from app import config

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Automated customer support response generator"""
    
    def __init__(self):
        # Default templates based on sentiment
        self.templates = {
            "positive": (
                "Dear {name},\n\n"
                "Thank you so much for your kind words! We are absolutely thrilled to hear that you had a "
                "great experience with {product}. Feedback like yours inspires us to keep delivering the "
                "best possible service.\n\n"
                "Please let us know if there's anything else we can assist you with!\n\n"
                "Best regards,\n"
                "Customer Support Team"
            ),
            "neutral": (
                "Dear {name},\n\n"
                "Thank you for contacting our customer support team regarding your query about {product}.\n\n"
                "We have received your ticket and our specialists are currently reviewing the details. "
                "We aim to provide a comprehensive update on your request within 24 hours.\n\n"
                "Best regards,\n"
                "Customer Support Team"
            ),
            "negative": (
                "Dear {name},\n\n"
                "We are sincerely sorry to hear about the difficulties you experienced with {product}. "
                "We understand your frustration and apologize for the inconvenience this has caused.\n\n"
                "Your issue is a priority for us. We have escalated this ticket to our technical "
                "engineering department to investigate and resolve it as quickly as possible.\n\n"
                "Thank you for your patience while we get this sorted out.\n\n"
                "Sincerely,\n"
                "Customer Support Team"
            )
        }

    def extract_keywords(self, text, max_keywords=3):
        """
        Extract key phrases or words from the text
        """
        if not text or not isinstance(text, str):
            return []
            
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            
            # Simple keyword extraction
            words = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            
            # Filter alphanumeric and non-stopwords
            keywords = [w for w in words if w.isalnum() and w not in stop_words and len(w) > 2]
            
            # Count frequencies
            freq = {}
            for kw in keywords:
                freq[kw] = freq.get(kw, 0) + 1
                
            sorted_kws = sorted(freq.items(), key=lambda x: x[1], reverse=True)
            return [k[0] for k in sorted_kws[:max_keywords]]
        except Exception:
            # Fallback split
            words = [w.lower() for w in text.split() if len(w) > 3]
            return list(set(words[:max_keywords]))

    def generate_response(self, subject, body, sentiment, customer_name="Customer", product_name="our service"):
        """
        Generate suggested reply draft dynamically using GenAI
        """
        sent = sentiment.lower() if sentiment else "neutral"
        if sent not in self.templates:
            sent = "neutral"
            
        reply = None
        
        # Prompt construction
        prompt = (
            f"You are a professional customer support agent for '{product_name}'. "
            f"Write a helpful and polite email reply to '{customer_name}' regarding their support ticket. "
            f"Ticket Subject: '{subject}'. "
            f"Customer's Message: '{body}'. "
            f"The detected sentiment of their message is {sent}. Tailor your empathy accordingly. "
            f"Return ONLY the email body text. Do not include placeholders or internal notes."
        )

        api_errors = []

        # 1. Try Google Gemini API if configured
        if config.GEMINI_API_KEY and config.GEMINI_API_KEY.strip() and "your_gemini" not in config.GEMINI_API_KEY.lower():
            try:
                import requests
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={config.GEMINI_API_KEY}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.7}
                }
                res = requests.post(gemini_url, headers=headers, json=payload, timeout=12)
                if res.status_code == 200:
                    reply = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                else:
                    api_errors.append(f"Gemini API Error {res.status_code}: {res.text}")
            except Exception as e:
                api_errors.append(f"Gemini Connection Failed: {e}")

        # 2. Try Hugging Face Chat Completion API if Gemini is not available or failed
        if not reply and config.HF_TOKEN and config.HF_TOKEN.strip() and "your_hf_token" not in config.HF_TOKEN.lower():
            try:
                import requests
                hf_url = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.HF_TOKEN}"
                }
                payload = {
                    "model": "Qwen/Qwen2.5-7B-Instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
                res = requests.post(hf_url, headers=headers, json=payload, timeout=15)
                if res.status_code == 200:
                    reply = res.json()['choices'][0]['message']['content'].strip()
                elif res.status_code == 503:
                    api_errors.append(f"Hugging Face model loading (503): {res.text}")
                else:
                    api_errors.append(f"Hugging Face API Error {res.status_code}: {res.text}")
            except Exception as e:
                api_errors.append(f"Hugging Face Connection Failed: {e}")

        # 3. Try Grok API if both free alternatives are not available/failed
        if not reply and config.GROK_API_KEY and config.GROK_API_KEY.strip() and "grok-beta" not in config.GROK_API_KEY.lower():
            try:
                import requests
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.GROK_API_KEY}"
                }
                payload = {
                    "model": "grok-2-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                res = requests.post(config.GROK_API_URL, headers=headers, json=payload, timeout=10)
                if res.status_code == 200:
                    reply = res.json()['choices'][0]['message']['content'].strip()
                else:
                    api_errors.append(f"Grok API Error {res.status_code}: {res.text}")
            except Exception as e:
                api_errors.append(f"Grok Connection Failed: {e}")

        # Compile api_error string for user visibility if generation failed
        if not reply:
            if api_errors:
                api_error = " | ".join(api_errors)
            else:
                api_error = "No valid API keys configured in .env file (Gemini, HF, or Grok)"
        else:
            api_error = None
        
        # Fallback to static template if API key is missing or request failed
        if not reply:
            template = self.templates[sent]
            reply = template.format(name=customer_name, product=product_name)
            if api_error:
                reply = f"[SYSTEM NOTE: AI Generation Failed. Reason: {api_error}. Falling back to static template.]\n\n" + reply
            
        keywords = self.extract_keywords(f"{subject} {body}")
        
        # Build additional suggestions based on sentiment
        suggestions = []
        if sent == "negative":
            suggestions.append("Apply discount or credit voucher.")
            suggestions.append("Escalate ticket to Senior Engineering Lead.")
        elif sent == "positive":
            suggestions.append("Invite customer to share review on social channels.")
            
        return {
            "base_response": reply,
            "keywords": keywords,
            "suggestions": suggestions
        }
