
# pipeline_lib.py

import pandas as pd

def check_for_nulls(df):
    """
    Check for null values in the dataframe.
    Returns a boolean indicating if nulls are present and the count of nulls.
    """
    nulls_present = df.isnull().values.any()  # Check if any nulls are present
    null_count = df.isnull().sum().sum()    # Count total nulls in the dataframe
    return nulls_present, null_count


def get_data_types(df):
    """
    Get the data types of each column in the dataframe.
    Returns a dictionary with column names as keys and their data types as values.
    """
    return df.dtypes.to_dict()  # Convert data types to a dictionary


def summarize_numerical_columns(df):
    """
    Generate summary statistics for numerical columns in the dataframe.
    Returns a dataframe containing summary statistics like mean, median, and standard deviation.
    """
    return df.describe()  # Get summary statistics for numerical columns


def check_for_duplicates(df):
    """
    Check for duplicate rows in the dataframe.
    Returns a boolean indicating if duplicates are present and the count of duplicate rows.
    """
    duplicates_present = df.duplicated().any()  # Check if any duplicates are present
    duplicate_count = df.duplicated().sum()    # Count total duplicate rows
    return duplicates_present, duplicate_count


