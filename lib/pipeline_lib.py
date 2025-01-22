
# pipeline_lib.py

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    This function takes a DataFrame and corrects spelling errors in all string columns.
    """
    # Iterate through each column in the DataFrame
    for col in df.columns:
        # Check if the column type is object (string)
        if df[col].dtype == 'object':
            # Apply the TextBlob spell check and correction
            df[col] = df[col].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


