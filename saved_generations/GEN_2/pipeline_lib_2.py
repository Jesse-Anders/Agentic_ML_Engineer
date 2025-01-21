
# pipeline_lib.py

import pandas as pd
from textblob import TextBlob

def fix_spelling(df):
    for column in df.columns:
        if df[column].dtype == 'object':  # Check if the column is of string type
            df[column] = df[column].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


