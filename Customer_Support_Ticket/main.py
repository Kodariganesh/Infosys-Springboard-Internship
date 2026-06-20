"""
Main CLI entry point for the Customer Support Ticket Management System
"""

import argparse
import sys
import os
import logging
import shutil
from app import config
from app.analysis.data_loader import load_data, clean_data, get_data_info
from app.sentiment.analyzer import HuggingFaceSentimentAnalyzer
from app.escalation.escalator import TicketEscalator
from app.responses.generator import ResponseGenerator

# Configure logging
log_file = config.LOG_DIR / "app.log"
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main")


def run_analysis():
    logger.info("--- Starting Data Analysis ---")
    try:
        df = load_data(config.DATA_CSV_PATH)
        info = get_data_info(df)
        logger.info(f"Loaded dataset from {config.DATA_CSV_PATH}")
        logger.info(f"Shape: {info['shape']}")
        logger.info(f"Columns: {info['columns']}")
        logger.info(f"Duplicate rows: {info['duplicate_rows']}")
        
        df_clean = clean_data(df)
        logger.info("Preprocessed and cleaned dataset successfully.")
        return df_clean
    except Exception as e:
        logger.error(f"Error in data analysis: {e}")
        raise e


def run_sentiment(df, sample_size=10):
    logger.info("--- Starting Sentiment Analysis ---")
    analyzer = HuggingFaceSentimentAnalyzer()
    
    # Determine column name
    desc_col = 'Ticket Description' if 'Ticket Description' in df.columns else 'body'
    if desc_col not in df.columns:
        desc_col = 'body' if 'body' in df.columns else df.select_dtypes(include=['object']).columns[0]
    
    samples = df.head(sample_size).copy()
    sentiments = []
    scores = []
    
    logger.info(f"Analyzing sentiment for {sample_size} sample tickets...")
    for idx, row in samples.iterrows():
        text = str(row.get(desc_col, ''))
        result = analyzer.analyze(text)
        sentiments.append(result['sentiment'])
        scores.append(result['score'])
        logger.debug(f"Ticket ID {idx} - Sentiment: {result['sentiment']} (Conf: {result['score']:.2f})")
        
    samples['predicted_sentiment'] = sentiments
    samples['predicted_score'] = scores
    
    # Summary count
    logger.info(f"Sentiment distribution: {samples['predicted_sentiment'].value_counts().to_dict()}")
    return samples


def run_escalation(df):
    logger.info("--- Starting Ticket Escalation Routing ---")
    escalator = TicketEscalator()
    df_escalated = escalator.escalate_tickets(df)
    
    escalated_only = df_escalated[df_escalated['escalated'] == True]
    logger.info(f"Identified {len(escalated_only)} tickets requiring immediate escalation.")
    
    for idx, row in escalated_only.head(5).iterrows():
        logger.info(f"Escalation Details [ID {idx}]: Reason: {row['escalation_reason']}")
        
    return df_escalated


def run_responses(df, sample_size=5):
    logger.info("--- Starting Auto-Response Generation ---")
    generator = ResponseGenerator()
    
    # Determine column names based on dataset format
    subject_col = 'Ticket Subject' if 'Ticket Subject' in df.columns else 'subject'
    body_col = 'Ticket Description' if 'Ticket Description' in df.columns else 'body'
    name_col = 'Customer Name' if 'Customer Name' in df.columns else 'customer_name'
    prod_col = 'Product Purchased' if 'Product Purchased' in df.columns else 'product'
    
    # Check if we have predicted sentiment, otherwise use placeholder sentiment
    sent_col = 'predicted_sentiment' if 'predicted_sentiment' in df.columns else 'sentiment'
    if sent_col not in df.columns:
        df = df.copy()
        df[sent_col] = 'neutral'
        
    samples = df.head(sample_size)
    logger.info(f"Generating draft support responses for {sample_size} samples...")
    
    for idx, row in samples.iterrows():
        subject = str(row.get(subject_col, ''))
        body = str(row.get(body_col, ''))
        sentiment = str(row.get(sent_col, 'neutral'))
        name = str(row.get(name_col, 'Customer'))
        product = str(row.get(prod_col, 'our product'))
        
        response = generator.generate_response(
            subject=subject,
            body=body,
            sentiment=sentiment,
            customer_name=name,
            product_name=product
        )
        
        logger.info(f"\n=========================================")
        logger.info(f"SUPPORT REPLY DRAFT FOR TICKET ID {idx}")
        logger.info(f"Customer: {name} | Sentiment: {sentiment.upper()}")
        logger.info(f"Extracted Keywords: {response['keywords']}")
        logger.info(f"Agent Actions: {response['suggestions']}")
        logger.info(f"-----------------------------------------")
        logger.info(response['base_response'])
        logger.info(f"=========================================\n")


def main():
    parser = argparse.ArgumentParser(description="Customer Support Ticket NLP & Escalation Management CLI")
    parser.add_argument(
        '--action',
        choices=['all', 'analyze', 'sentiment', 'escalate', 'respond'],
        default='all',
        help='The action/module pipeline to run.'
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=10,
        help='Number of samples to process in sentiment/response generation (default: 10).'
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting pipeline action: {args.action.upper()}")
    
    try:
        # Check if CSV file is present
        if not os.path.exists(config.DATA_CSV_PATH):
            # Try to copy a sample CSV from rough/ directory if available
            rough_csv = None
            rough_dir = config.PROJECT_ROOT / "rough"
            if not rough_dir.exists():
                rough_dir = config.PROJECT_ROOT / "Customer_Support_Ticket" / "rough"
                
            for root, dirs, files in os.walk(rough_dir):
                for file in files:
                    if file.endswith('.csv'):
                        rough_csv = os.path.join(root, file)
                        break
            if rough_csv:
                logger.info(f"Found sample CSV in rough folder: {rough_csv}. Copying to {config.DATA_CSV_PATH}")
                shutil.copy(rough_csv, config.DATA_CSV_PATH)
            else:
                logger.error(f"Please place your dataset file at: {config.DATA_CSV_PATH}")
                sys.exit(1)
                
        df_clean = run_analysis()
        
        if args.action == 'analyze':
            return
            
        df_sent = df_clean
        if args.action in ['sentiment', 'all', 'respond']:
            df_sent = run_sentiment(df_clean, sample_size=args.sample_size)
            
        df_esc = df_clean
        if args.action in ['escalate', 'all']:
            df_esc = run_escalation(df_sent)
            
        if args.action in ['respond', 'all']:
            # Use the sentiment-analyzed dataframe
            run_responses(df_sent, sample_size=min(args.sample_size, 5))
            
        logger.info("Pipeline executed successfully!")
        
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
