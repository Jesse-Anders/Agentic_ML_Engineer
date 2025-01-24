
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    Fixes spelling errors in the DataFrame.
    Applies TextBlob to each cell to correct spelling.
    """
    # Iterate over each column in the DataFrame
    for col in df.columns:
        # Apply the TextBlob correction to each cell
        df[col] = df[col].apply(lambda x: str(TextBlob(str(x)).correct()))
    return df


def remove_duplicates(df):
    """
    Remove duplicate rows from the DataFrame.
    
    Parameters:
    df (pd.DataFrame): The DataFrame from which to remove duplicates.
    
    Returns:
    pd.DataFrame: A DataFrame with duplicates removed.
    """
    # Use the drop_duplicates method to remove duplicates
    return df.drop_duplicates()


