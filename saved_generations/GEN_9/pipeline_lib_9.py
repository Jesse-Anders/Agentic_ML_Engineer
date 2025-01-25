
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    # Iterate over each column in the DataFrame
    for col in df.columns:
        # Check if the column is of type object (string)
        if df[col].dtype == 'object':
            # Apply the text correction to each element in the column
            df[col] = df[col].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
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
    # Use the drop_duplicates method to remove duplicate rows
    return df.drop_duplicates()


def handle_null_values(df):
    """
    This function handles null values in the DataFrame by filling them with the mean for numerical columns
    and the mode for categorical columns.
    """
    # Iterate through each column in the DataFrame
    for column in df.columns:
        if df[column].dtype == 'object':  # Check for categorical columns
            # Fill null values with the mode
            df[column].fillna(df[column].mode()[0], inplace=True)
        else:  # Assume numerical columns
            # Fill null values with the mean
            df[column].fillna(df[column].mean(), inplace=True)
    return df


