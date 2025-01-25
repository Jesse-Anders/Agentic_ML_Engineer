
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    This function takes a DataFrame and corrects spelling errors in all string columns.
    """
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


def remove_duplicates(df):
    """Remove duplicate rows from the DataFrame.
    
    Args:
        df (pd.DataFrame): The DataFrame from which to remove duplicates.
    
    Returns:
        pd.DataFrame: A DataFrame with duplicates removed.
    """
    # Use the drop_duplicates method to remove duplicate rows
    return df.drop_duplicates()


def handle_null_values(df):
    """
    This function handles null values in the dataframe.
    It fills null values with the mean for numerical columns and the mode for categorical columns.
    """
    # Fill null values in numerical columns with the mean
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
    
    # Fill null values in categorical columns with the mode
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])
    
    return df


