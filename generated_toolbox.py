import pandas as pd
from spellchecker import SpellChecker

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
