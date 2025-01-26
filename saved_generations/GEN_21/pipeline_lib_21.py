
# pipeline_lib.py

import pandas as pd


def check_column_data_type(df: pd.DataFrame, column_name: str) -> str:
    """
    Check the data type of a specified column in the DataFrame.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to check.
    column_name (str): The name of the column to check.
    
    Returns:
    str: The data type of the specified column.
    """
    # Check if the column exists in the DataFrame
    if column_name in df.columns:
        # Return the data type of the column
        return str(df[column_name].dtype)
    else:
        return 'Column not found'


