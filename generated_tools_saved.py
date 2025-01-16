# Saved this generated code for fixing spelling errors
import pandas as pd

from textblob import TextBlob
def fix_spelling_errors(df):
    for column in df.select_dtypes(include=['object']).columns:
        df[column] = df[column].apply(lambda x: str(TextBlob(x).correct()) if pd.notnull(x) else x)
    return df

import pandas as pd


# Another successfully generated function to fix spelling errors
import pandas as pd
from textblob import TextBlob

def fix_spelling_errors(df):
    """
    Fixes spelling errors in the DataFrame by applying a correction to each string entry.
    Assumes all columns are of string type for simplicity.
    """
    def correct_spelling(text):
        if isinstance(text, str):
            return str(TextBlob(text).correct())
        return text

    # Apply the correction function to each element in the DataFrame
    return df.applymap(correct_spelling)






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