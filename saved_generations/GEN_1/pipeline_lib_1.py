
# pipeline_lib.py

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    This function takes a DataFrame and checks each string entry for spelling errors.
    It corrects any spelling errors found and returns the modified DataFrame.
    """
    # Iterate over each column in the DataFrame
    for col in df.columns:
        # Check if the column is of string type
        if df[col].dtype == 'object':
            # Apply the spelling correction
            df[col] = df[col].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


def remove_duplicates(df):
    """
    Remove duplicate rows from the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame from which to remove duplicates.

    Returns:
    pd.DataFrame: A DataFrame with duplicates removed.
    """
    # Use the drop_duplicates method to remove duplicate rows
    return df.drop_duplicates()


