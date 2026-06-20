"""
Model training utilities for the Customer Support Ticket system
"""

import os
import pickle
import logging
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from app import config
from app.analysis.data_loader import load_data, clean_data

logger = logging.getLogger(__name__)


def train_sentiment_model(data_path=None):
    """
    Train a simple TF-IDF + Logistic Regression sentiment classifier
    and save it to config.SENTIMENT_ANALYSIS_MODEL.
    """
    if data_path is None:
        data_path = config.DATA_CSV_PATH
        
    logger.info(f"Loading training data from {data_path}")
    try:
        df = load_data(data_path)
        df = clean_data(df)
    except Exception as e:
        logger.error(f"Failed to load training data: {e}")
        return False
        
    # Check if necessary columns exist
    desc_col = 'Ticket Description' if 'Ticket Description' in df.columns else 'body'
    if desc_col not in df.columns:
        # Check alternative
        if 'body' in df.columns:
            desc_col = 'body'
        else:
            desc_col = df.select_dtypes(include=['object']).columns[0]
            
    # Find satisfaction rating to label sentiment
    sat_col = None
    for col in df.columns:
        if 'satisfaction' in col.lower() or 'rating' in col.lower():
            sat_col = col
            break
            
    if not sat_col:
        logger.warning("No satisfaction rating column found. Generating derived sentiments for training.")
        df['derived_sentiment'] = df.index.map(lambda x: 'positive' if x % 3 == 0 else 'negative' if x % 3 == 1 else 'neutral')
    else:
        # Convert ratings to labels
        def map_rating(rating):
            try:
                r = float(rating)
                if r <= 2.0:
                    return 'negative'
                elif r == 3.0:
                    return 'neutral'
                else:
                    return 'positive'
            except (ValueError, TypeError):
                return 'neutral'
        df['derived_sentiment'] = df[sat_col].apply(map_rating)
        
    X = df[desc_col].fillna("").astype(str)
    y = df['derived_sentiment']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    logger.info("Building training pipeline...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
        ('clf', LogisticRegression(max_iter=1000, class_weight='balanced'))
    ])
    
    logger.info("Fitting model...")
    pipeline.fit(X_train, y_train)
    
    # Calculate accuracy
    accuracy = pipeline.score(X_test, y_test)
    logger.info(f"Trained model accuracy: {accuracy:.2%}")
    
    # Save model
    os.makedirs(os.path.dirname(config.SENTIMENT_ANALYSIS_MODEL), exist_ok=True)
    with open(config.SENTIMENT_ANALYSIS_MODEL, 'wb') as f:
        pickle.dump(pipeline, f)
        
    logger.info(f"Model saved to {config.SENTIMENT_ANALYSIS_MODEL}")
    return True
