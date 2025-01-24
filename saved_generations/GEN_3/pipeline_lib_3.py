
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    This function takes a DataFrame and corrects spelling errors in all string columns.
    It uses TextBlob for spell checking and correction.
    """
    for col in df.select_dtypes(include=['object']).columns:
        # Apply the spelling correction to each entry in the column
        df[col] = df[col].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


def remove_duplicates(df):
    """
    Removes duplicate rows from the DataFrame.
    
    Parameters:
    df : pandas.DataFrame
        The DataFrame from which duplicates will be removed.
    
    Returns:
    pandas.DataFrame
        A DataFrame with duplicate rows removed.
    """
    # Use the drop_duplicates method to remove duplicates
    return df.drop_duplicates()



def handle_null_values(df: pd.DataFrame) -> pd.DataFrame:
    """Function to handle null values in a DataFrame."""
    # Fill null values with the mean of each column for numerical columns
    for column in df.select_dtypes(include=['float64', 'int64']).columns:
        df[column].fillna(df[column].mean(), inplace=True)
    # Fill null values with the mode for categorical columns
    for column in df.select_dtypes(include=['object']).columns:
        df[column].fillna(df[column].mode()[0], inplace=True)
    return df



