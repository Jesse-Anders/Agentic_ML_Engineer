
# pipeline_lib.py

from textblob import TextBlob

def fix_spelling_errors(df):
    """
    Fixes spelling errors in all string entries of the DataFrame.
    Uses TextBlob for spell checking and correction.
    """
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: ' '.join([str(TextBlob(word).correct()) for word in x.split()]) if isinstance(x, str) else x)
    return df


# Function to save the successful code

def save_successful_code(df):
    """
    Saves the changes made to the DataFrame after correcting spelling errors.
    """
    # Assuming we want to save the DataFrame as a CSV file
    df.to_csv('corrected_dataframe.csv', index=False)



