
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    """Fixes spelling errors in the DataFrame's string columns."""
    # Iterate through each column in the DataFrame
    for col in df.columns:
        # Check if the column is of string type
        if df[col].dtype == 'object':
            # Apply the spelling correction using TextBlob
            df[col] = df[col].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


def remove_duplicates(df):
    """
    Removes duplicate rows from the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame from which to remove duplicates.

    Returns:
    pd.DataFrame: A DataFrame with duplicates removed.
    """
    # Use the drop_duplicates method to remove duplicate rows
    return df.drop_duplicates()



def handle_null_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function handles null values in the DataFrame by:
    - Filling them with the mean for numerical columns.
    - Filling them with the mode for categorical columns.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame with potential null values.
    
    Returns:
    pd.DataFrame: A DataFrame with null values handled.
    """
    # Iterate through each column in the DataFrame
    for column in df.columns:
        if df[column].dtype == 'object':  # Categorical column
            # Fill null values with the mode
            df[column].fillna(df[column].mode()[0], inplace=True)
        else:  # Numerical column
            # Fill null values with the mean
            df[column].fillna(df[column].mean(), inplace=True)
    return df


