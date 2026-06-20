#!/bin/bash
# Quick start script for Customer Support Ticket System (Linux/macOS)

echo "========================================="
echo "Customer Support Ticket System - Setup"
echo "========================================="

# Check Python version
echo ""
echo "Checking Python installation..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Download NLTK data
echo ""
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"

echo ""
echo "========================================="
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create .env file from .env.example"
echo "2. Place your data in data/ directory"
echo "3. Run: python main.py --action all"
echo "========================================="
