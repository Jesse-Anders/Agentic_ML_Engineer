# toolbox.py

import pandas as pd
from logging_utils import log_transformation

@log_transformation("drop_duplicate_rows")
def drop_duplicate_rows(df):
    """
    Remove duplicate rows from the DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to remove duplicates from.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with duplicates removed.
    
    Notes
    -----
    Logging is automatically handled by the @log_transformation decorator, 
    which records metadata in a JSON file.
    """
    # Perform the actual dropping of duplicates
    return df.drop_duplicates()
