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
        "Average Entry Length in Characters (High Averages Indicate Likely NLP)": average_entry_length,
        "Top 5 Value Counts": top_values_dict,
        f"Sampling of Entries (length capped at {sample_length})": truncated_samples
    }

    return column_info

# Initialize a global dictionary to store mappings for each encoded column
column_mappings = {}

# Encode Categorical Features
def execute_numeric_encode(df, column_name):
    global column_mappings  # Reference the global dictionary
    
    # Check if the column exists in the DataFrame
    if column_name not in df.columns:
        print(f"Column '{column_name}' not found in DataFrame. Skipping...")
        return df
    
    # Get unique values and sort them to ensure consistent mapping
    unique_values = sorted(df[column_name].unique())
    
    # Create a mapping dictionary from unique value to an integer code
    mapping_dict = {val: idx for idx, val in enumerate(unique_values)}
    
    # Create the encoded column name
    encoded_column_name = f'encoded_{column_name}'
    
    # Apply the mapping to create a new encoded column
    df[encoded_column_name] = df[column_name].replace(mapping_dict)
    
    # Drop the original column
    #df.drop(columns=[column_name], inplace=True)
    
    # Store the mapping using the encoded column name as a reference
    column_mappings[encoded_column_name] = mapping_dict

    print(f"Created encoded_{column_name}")
    print(f"Encoded as {column_mappings[encoded_column_name]}")
    print()

    return df

# Example usage
# Assuming 'df' is your DataFrame and 'column_to_encode' is the column you want to encode
# df = encode_column(df, 'education_level')
# print(column_mappings['education_level'])  # Access the stored mapping

