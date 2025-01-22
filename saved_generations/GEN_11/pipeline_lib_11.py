
# pipeline_lib.py

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    Fixes spelling errors in the DataFrame by applying TextBlob to each cell.
    """
    for col in df.columns:
        df[col] = df[col].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


