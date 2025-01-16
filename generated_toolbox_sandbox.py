from textblob import TextBlob
import pandas as pd

def fix_spelling_errors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fixes spelling errors in a DataFrame by applying TextBlob's correction method to string entries.
    Assumes that the DataFrame primarily contains text data.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to process.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with corrected spelling.
    """
    def correct_spelling(text):
        try:
            return str(TextBlob(text).correct())
        except Exception:
            return text

    # Apply the correction function to all string entries in the DataFrame
    return df.applymap(lambda x: correct_spelling(x) if isinstance(x, str) else x)