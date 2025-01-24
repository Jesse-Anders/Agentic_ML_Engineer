
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    Function to fix spelling errors in the DataFrame.
    Assumes that the DataFrame contains text data that may have spelling errors.
    """
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Assuming we want to fix spelling in all string columns
        for col in df.select_dtypes(include=['object']).columns:
            # Check if the cell is a string before correcting
            if isinstance(row[col], str):
                # Fix the spelling errors using TextBlob
                corrected_text = str(TextBlob(row[col]).correct())
                # Update the DataFrame with corrected text
                df.at[index, col] = corrected_text
    return df


def remove_duplicates(df):
    """
    Remove duplicate rows from the DataFrame.
    
    Parameters:
    df : pandas.DataFrame
        The DataFrame from which to remove duplicates.
    
    Returns:
    pandas.DataFrame
        A DataFrame with duplicates removed.
    """
    # Using the drop_duplicates method to remove duplicate rows
    return df.drop_duplicates()


def handle_null_values(df):
    """
    This function takes a DataFrame and handles null values by filling them
    with the mean of their respective columns for numerical columns and
    with the mode for categorical columns.
    """
    # Fill numeric columns with the mean
    for column in df.select_dtypes(include=['float64', 'int64']).columns:
        df[column].fillna(df[column].mean(), inplace=True)

    # Fill categorical columns with the mode
    for column in df.select_dtypes(include=['object']).columns:
        df[column].fillna(df[column].mode()[0], inplace=True)

    return df


