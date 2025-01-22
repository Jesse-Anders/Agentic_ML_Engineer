from textblob import TextBlob
import pandas as pd

def fix_spelling_errors(df, column_name):
    """
    Fixes spelling errors in the specified column of a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    column_name (str): The name of the column to correct spelling errors in.

    Returns:
    pd.DataFrame: The DataFrame with corrected spelling in the specified column.
    """
    # Apply the TextBlob correction to each entry in the specified column
    df[column_name] = df[column_name].apply(lambda x: str(TextBlob(x).correct()))
    return df

# Example of how to call the function
# df = fix_spelling_errors(df, 'your_column_name')

df = fix_spelling_errors(df, 'your_column_name') # Replace 'your_column_name' with the actual column name

