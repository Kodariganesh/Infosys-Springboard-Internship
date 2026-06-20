"""
Data loading and preprocessing utilities
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_data(file_path):
    """
    Load CSV data from file
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        pandas DataFrame
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    return df


def clean_data(df):
    """
    Clean and preprocess data
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    # Identify column types
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    # Fill missing values
    if len(numerical_cols) > 0:
        df[numerical_cols] = df[numerical_cols].fillna(df[numerical_cols].mean())
    if len(categorical_cols) > 0:
        df[categorical_cols] = df[categorical_cols].fillna(df[categorical_cols].mode().iloc[0])
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    return df


def get_data_info(df):
    """
    Get information about the dataset
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with data statistics
    """
    return {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum()
    }
