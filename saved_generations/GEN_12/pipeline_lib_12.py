
# pipeline_lib.py

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    This function takes a DataFrame and fixes any spelling errors in its string columns.
    """
    for col in df.columns:
        if df[col].dtype == 'object':  # Check if the column is of string type
            df[col] = df[col].apply(lambda x: ' '.join([str(TextBlob(word).correct()) for word in x.split()]) if isinstance(x, str) else x)
    return df


