
# pipeline_lib.py

import pandas as pd
from textblob import TextBlob

def fix_spelling(df):
    for col in df.columns:
        if df[col].dtype == 'object':  # check if the column is of string type
            df[col] = df[col].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


