
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    This function takes a DataFrame and checks each cell for spelling errors.
    It corrects any errors found using TextBlob and returns the modified DataFrame.
    """
    # Iterate through each column in the DataFrame
    for col in df.columns:
        # Apply the correction to each cell in the column
        df[col] = df[col].apply(lambda x: str(TextBlob(str(x)).correct()) if isinstance(x, str) else x)
    return df


def remove_duplicates(df):
    """
    This function removes duplicate rows from the given DataFrame.
    
    Parameters:
    df : pandas.DataFrame
        The DataFrame from which duplicates will be removed.
    
    Returns:
    pandas.DataFrame
        A DataFrame with duplicates removed.
    """
    # Use the drop_duplicates method to remove duplicates
    return df.drop_duplicates()



def handle_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Handles null values in the DataFrame by filling them with the mean for numerical columns and the mode for categorical columns."""
    # Iterate through each column in the DataFrame
    for column in df.columns:
        if df[column].dtype == 'object':  # Categorical column
            # Fill nulls with the mode of the column
            df[column].fillna(df[column].mode()[0], inplace=True)
        else:  # Numerical column
            # Fill nulls with the mean of the column
            df[column].fillna(df[column].mean(), inplace=True)
    return df


