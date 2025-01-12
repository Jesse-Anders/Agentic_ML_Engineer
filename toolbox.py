# toolbox.py

import os
import pandas as pd
from typing import Annotated
from langchain_core.tools import tool

def drop_duplicated(df: pd.DataFrame) -> str:
    """
    function_name = drop_duplicated

    Description: A simple function that drops duplicate rows from a DataFrame in place and returns a summary string.
    """
    if not isinstance(df, pd.DataFrame):
        return "Error: input is not a valid pandas DataFrame."

    initial_len = len(df)
    df.drop_duplicates(inplace=True)
    final_len = len(df)
    return f"Dropped {initial_len - final_len} duplicate rows. Remaining rows: {final_len}."

def what_the():
    """
    function_name = what_the
    Description: A function to be avoided.
    It does nothing
    """
    return
