
# pipeline_lib.py

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    This function takes a DataFrame and corrects spelling errors in all string entries.
    It uses TextBlob for spell checking and correction.
    """
    # Iterate through each column in the DataFrame
    for column in df.columns:
        # Check if the column is of type object (string)
        if df[column].dtype == 'object':
            # Apply the spelling correction to each entry in the column
            df[column] = df[column].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


def remove_duplicates(df):
    """
    Removes duplicate rows from the DataFrame.
    
    Parameters:
    df: pandas DataFrame
        The DataFrame from which to remove duplicates.
    
    Returns:
    pandas DataFrame
        A DataFrame with duplicate rows removed.
    """
    # Using the drop_duplicates method to remove duplicates
    return df.drop_duplicates()


