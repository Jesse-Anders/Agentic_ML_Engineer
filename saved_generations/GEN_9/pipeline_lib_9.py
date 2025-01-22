
# pipeline_lib.py

from textblob import TextBlob

def fix_spelling_errors(df):
    """Fixes spelling errors in all string columns of the DataFrame."""
    for col in df.select_dtypes(include=['object']).columns:
        # Apply the TextBlob correction to each entry in the column
        df[col] = df[col].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


