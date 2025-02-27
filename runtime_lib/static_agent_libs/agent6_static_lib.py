import pandas as pd
import sys
import os
import json
from tqdm import tqdm
from agent_builds.base_agents import basic_agent

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Shared State Getters
# from utils import get_dataframe_stage, get_target_column, get_current_column
from utils import get_dataframe_stage, get_shared_var, print_stream


def gather_column_info(df, sample_count=10, sample_length=300):
    """
    Gathers and returns key information about the current column,
    such as data type, number of unique values, missing values,
    top value counts, a ratio of unique values to total rows,
    average entry length, and truncated samples.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the column.
    sample_count : int, optional
        Number of sample rows to retrieve.
    sample_length : int, optional
        Maximum number of characters to include for each sample value.

    Returns
    -------
    dict
        A dictionary containing column metadata useful for encoding decisions.
    """
    # Retrieve the current column from your shared variable system
    column = get_shared_var('current_column')

    # Validate column existence
    if column not in df.columns:
        return {
            "column_name": column,
            "error": f"Column '{column}' not found in DataFrame."
        }

    col_data = df[column]

    # Basic stats
    dtype = str(col_data.dtype)
    num_unique = col_data.nunique(dropna=True)
    total_rows = len(col_data)
    
    # Compute ratio of unique values to total rows
    unique_to_total_ratio = num_unique / total_rows if total_rows else 0.0

    # Compute average entry length (only for non-null entries)
    non_null_values = col_data.dropna().astype(str)
    average_entry_length = sum(len(entry) for entry in non_null_values) / len(non_null_values) if len(non_null_values) > 0 else 0

    # Top 5 value counts
    top_values_series = col_data.value_counts(dropna=False).head(5)
    top_values_dict = top_values_series.to_dict()

    # Sample data (truncated)
    sample_series = non_null_values.head(sample_count)
    truncated_samples = [val[:sample_length] for val in sample_series]

    # Construct the info dictionary
    column_info = {
        "Column Name": column,
        "Data Type": dtype,
        "Number of Unique Values": num_unique,
        "Total Rows": total_rows,
        "Ratio of Unique Entries to Total Entries (Lower Value Indicates More Likely Categorical)": unique_to_total_ratio,
        "Average Entry Length in Characters (Above 50 Indicates Very Likely NLP)": average_entry_length,
        "Top 5 Value Counts": top_values_dict,
        f"Sampling of Entries (length capped at {sample_length})": truncated_samples
    }

    return column_info

# Encode Categorical Features
def execute_numeric_encode(df, column, column_mappings):
    """
    Perform numeric encoding on a categorical column and update column_mappings.
    
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    - column (str): The column to encode.
    - column_mappings (dict): The global dictionary to store encoding mappings.
    
    Returns:
    - pd.DataFrame: Updated DataFrame with numeric encoding.
    - dict: Updated column_mappings dictionary.
    """
    
    # Check if the column exists in the DataFrame
    if column not in df.columns:
        print(f"Column '{column}' not found in DataFrame. Skipping...")
        return df, column_mappings  # Return without modification
    
    # Get unique values and sort them to ensure consistent mapping
    unique_values = sorted(df[column].dropna().unique())  # Drop NaN to avoid issues
    
    # Create a mapping dictionary from unique value to an integer code
    mapping_dict = {val: idx for idx, val in enumerate(unique_values)}
    
    # Create the encoded column name
    encoded_column_name = f'{column}_Numeric_Encoded'
    
    # Apply the mapping to create a new encoded column
    df[encoded_column_name] = df[column].replace(mapping_dict)
    
    # Drop the original column
    df.drop(columns=[column], inplace=True)
    
    # Update column_mappings dictionary
    column_mappings[encoded_column_name] = mapping_dict

    print(f"Created {encoded_column_name}")
    print(f"Encoded as {column_mappings[encoded_column_name]}")

    return df, column_mappings


# Example usage
# Assuming 'df' is your DataFrame and 'column_to_encode' is the column you want to encode
# df = encode_column(df, 'education_level')
# print(column_mappings['education_level'])  # Access the stored mapping


# MIN/MAX NORMALIZATION
# Creates a new Column with min/max normalization
def execute_scaling_normalization(df, column, column_mappings):
    """
    Apply min-max normalization to a specific column in a pandas DataFrame and create a new column for the normalized values.

    Parameters:
    - df: pandas DataFrame
    - column: The column to normalize

    The function will add a new column to the DataFrame with the normalized values, prefixed with 'mm_'.
    """
    thisThing = column_mappings
    # Apply min-max normalization
    min_value = df[column].min()
    max_value = df[column].max()
    df[column + '_Normalized'] = (df[column] - min_value) / (max_value - min_value)
    
        # Drop the original column
    df.drop(columns=[column], inplace=True)

    print(f"Created {column}_Normalized")

# Example usage:
# min_max_normalize_column(df, 'column_to_normalize')
# After this, df will have a new column with the name 'mm_column_to_normalize' containing the normalized values.
