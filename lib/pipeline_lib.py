
# pipeline_lib.py

import pandas as pd
from textblob import TextBlob

def fix_spelling_errors(df):
    for column in df.select_dtypes(include=['object']).columns:
        df[column] = df[column].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


