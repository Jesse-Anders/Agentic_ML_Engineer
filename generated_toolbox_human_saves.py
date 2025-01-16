# Saved this generated code for fixing spelling errors
import pandas as pd
from textblob import TextBlob

def fix_spelling_errors(df):
    """
    Fixes spelling errors in string columns of the DataFrame.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to process.
    
    Returns:
    pd.DataFrame: The DataFrame with corrected spelling in string columns.
    """
    for column in df.select_dtypes(include=['object']).columns:
        df[column] = df[column].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df

# Another successfully generated function to fix spelling errors


from spellchecker import SpellChecker


# 1/14 JAND - UNTESTED SPELL CHECKER!! INSTALL MODULE AND TEST
# Initialize the spell checker
spell = SpellChecker()

def fix_spelling_errors(df):
    """
    Fixes spelling errors in the DataFrame by checking each string value.
    Assumes all columns are of type string or contain string values.
    """
    # Iterate over each column in the DataFrame
    for column in df.columns:
        # Apply spell correction to each element in the column if it's a string
        df[column] = df[column].apply(lambda x: ' '.join([spell.correction(word) for word in x.split()]) if isinstance(x, str) else x)
    return df