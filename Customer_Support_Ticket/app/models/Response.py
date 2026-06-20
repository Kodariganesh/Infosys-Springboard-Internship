"""
Automated response generation wrapper (Response.py)
"""
from app.responses.generator import ResponseGenerator
from app.models.Sentiment import get_sentiment

def automate_response(title: str, body: str, customer_name: str = "Customer", product_name: str = "our service"):
    generator = ResponseGenerator()
    # Fetch sentiment for the template mapping
    sent_res = get_sentiment(title, body)
    sent_str = sent_res.get("sentiment", "Neutral").lower()
    
    mapped_sentiment = "neutral"
    if "positive" in sent_str:
        mapped_sentiment = "positive"
    elif "negative" in sent_str:
        mapped_sentiment = "negative"
        
    res = generator.generate_response(
        title, 
        body, 
        mapped_sentiment, 
        customer_name=customer_name, 
        product_name=product_name
    )
    
    subject = f"Re: {title}"
    body_content = res.get("base_response", "")
    return subject, body_content
