from textblob import TextBlob
import pandas as pd

def fix_spelling_errors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fixes spelling errors in a DataFrame by applying TextBlob's correction method to string columns.
    Assumes that the DataFrame 'df' is already loaded in the environment.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to process.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with corrected spelling errors.
    """
    # Iterate over each column in the DataFrame
    for column in df.columns:
        # Check if the column is of type object (string)
        if df[column].dtype == "object":
            # Apply TextBlob's correction to each entry in the column
            df[column] = df[column].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df