import pandas as pd
from textblob import TextBlob

def fix_spelling_errors(df):
    """
    Fixes spelling errors in string columns of the DataFrame.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to process.
    
    Returns:
    pd.DataFrame: The DataFrame with corrected spelling in string columns.
    """
    for column in df.select_dtypes(include=['object']).columns:
        df[column] = df[column].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df
