# No unreviewed generated code is contained in this file

# Every function should ideally have a [description]: field within its docstring

import pandas as pd

def drop_df_duplicates(df):
    '''
    [description]: Drops duplicate rows from a DataFrame "in place"
    '''
    start_rows = len(df)
    df.drop_duplicates(inplace=True)
    end_rows = len(df)

    return f'Dropped {start_rows - end_rows} duplicate rows. There are {end_rows} remaining rows.'

# static_lib.py
def data_type_check(df, column_name) -> str:
    """
    Checks the data type of the given column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame.
        column_name (str): The name of the column to check.

    Returns:
        str: A message describing the column's data type.
    """
    column = df[column_name]  # Access the column dynamically
    column_dtype = column.dtype

    if column_dtype == 'object':
        return f"Column '{column_name}' contains text data (dtype: {column_dtype})."
    elif column_dtype in ['int64', 'float64']:
        return f"Column '{column_name}' contains numeric data (dtype: {column_dtype})."
    elif column_dtype == 'bool':
        return f"Column '{column_name}' contains boolean data (dtype: {column_dtype})."
    else:
        return f"Column '{column_name}' has an unhandled data type: {column_dtype}."
