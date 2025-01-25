
# pipeline_lib.py

import pandas as pd

def check_nulls(df):
    """
    This function checks for null values in the DataFrame.
    Returns a boolean indicating if nulls are present and the count of nulls.
    """
    null_count = df.isnull().sum().sum()  # Count total nulls in the DataFrame
    has_nulls = null_count > 0  # Check if there are any nulls
    return has_nulls, null_count  # Return a tuple of the result and the count


def get_data_types(df):
    """
    This function retrieves the data types of each column in the DataFrame.
    Returns a dictionary with column names as keys and data types as values.
    """
    return df.dtypes.to_dict()  # Convert data types to a dictionary


def describe_data(df):
    """
    This function provides a summary of the DataFrame, including count, mean, std, min, 25%, 50%, 75%, and max for numeric columns.
    Returns the summary statistics as a DataFrame.
    """
    return df.describe()  # Generate descriptive statistics


