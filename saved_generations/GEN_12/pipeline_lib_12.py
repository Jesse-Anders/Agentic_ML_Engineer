
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Iterate through each column in the row
        for col in df.columns:
            if isinstance(row[col], str):  # Check if the value is a string
                # Correct the spelling using TextBlob
                corrected_text = str(TextBlob(row[col]).correct())
                df.at[index, col] = corrected_text  # Update the DataFrame with corrected text
    return df


def remove_duplicates(df):
    """
    This function removes duplicates from the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame from which to remove duplicates.

    Returns:
    pd.DataFrame: A DataFrame with duplicates removed.
    """
    # Remove duplicates and return the cleaned DataFrame
    return df.drop_duplicates()


def handle_null_values(df):
    """
    This function handles null values in the DataFrame by filling them with the mean of their respective columns for numeric columns,
    and filling non-numeric columns with the mode (most frequent value).
    
    Parameters:
    df (pd.DataFrame): The input DataFrame with potential null values.
    
    Returns:
    pd.DataFrame: A DataFrame with null values filled.
    """
    # Fill null values for numeric columns with the mean
    for column in df.select_dtypes(include=['float64', 'int64']):
        df[column].fillna(df[column].mean(), inplace=True)
    
    # Fill null values for non-numeric columns with the mode
    for column in df.select_dtypes(include=['object']):
        df[column].fillna(df[column].mode()[0], inplace=True)
    
    return df


