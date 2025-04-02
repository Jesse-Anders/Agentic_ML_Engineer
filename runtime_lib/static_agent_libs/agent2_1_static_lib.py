from collections import Counter
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from scipy.stats import chi2_contingency
import json
import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Shared State Getters
from utils import get_dataframe_stage, get_shared_var

def populate_redundancy_json(file_path='json_lib/saved_redundancy_dictionary.json'):
    """
    Retrieves the redundancy dictionary from shared state and writes it to a JSON file.
    
    This function pulls the dictionary using get_shared_var('redundancy_dictionary') and
    writes it to disk, ensuring the directory exists.

    Args:
        file_path (str): Destination path for the JSON file. Defaults to 'json_lib/saved_redundancy_dictionary.json'.
    
    Returns:
        str: Status message indicating success or failure.
    """
    # Retrieve the redundancy dictionary from shared memory (LangGraph state)
    redundancy_dictionary = get_shared_var('redundancy_dictionary')
    
    # If no dictionary is found, do not proceed
    if not redundancy_dictionary:
        print("No redundancy dictionary found in shared state.")
        return "No redundancy dictionary found in shared state."

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the dictionary to the JSON file
    with open(file_path, 'w') as file:
        json.dump(redundancy_dictionary, file, indent=4)

    print(f"Redundancy dictionary saved to {file_path}")
    return f"Redundancy dictionary saved to {file_path}"


def display_redundancy_json():
    """
    Retrieves the redundancy dictionary from shared state and returns it
    as a formatted JSON string for display purposes.

    Returns:
        str: Pretty-printed JSON string of the redundancy dictionary,
             or a message if nothing is found.
    """
    redundancy_dictionary = get_shared_var('redundancy_dictionary')

    if not redundancy_dictionary:
        return "No redundancy dictionary found in shared state."

    # Return as a human-readable formatted JSON string
    return json.dumps(redundancy_dictionary, indent=4)


def clean_redundant_entries(df):
    """
    Cleans redundant entries in a specified DataFrame column by mapping them to their canonical key.
    
    This function loads the column-specific redundancy dictionary from a JSON file located at
    'json_lib/saved_redundancy_dictionary.json'. It then retrieves the current column name via 
    get_shared_var('current_column') and constructs a mapping from each redundant variant to its canonical key.
    Finally, it applies this mapping to update the DataFrame column.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the column to be cleaned.
        
    Returns:
        pd.DataFrame: The updated DataFrame with redundant entries replaced by their canonical key.
    """
    # Retrieve the current column name
    column = get_shared_var('current_column')
    
    # Define the file path for the redundancy JSON file
    file_path = 'json_lib/saved_redundancy_dictionary.json'
    
    # Check if the JSON file exists
    if not os.path.exists(file_path):
        print("JSON file with redundancy dictionary not found. No changes applied.")
        return "JSON file with redundancy dictionary not found. No changes applied."
    
    # Load the redundancy dictionary from the JSON file
    with open(file_path, 'r') as file:
        redundancy_dict = json.load(file)
    
    # If no dictionary exists for the current column, do nothing
    if column not in redundancy_dict:
        print(f"No redundancy dictionary found for column '{column}'. No changes applied.")
        return f"No redundancy dictionary found for column '{column}'. No changes applied."
    
    # Build the mapping: for each canonical key in the current column's dictionary,
    # map each redundant variant to the canonical key.
    mapping = {}
    for canonical_key, redundant_values in redundancy_dict[column].items():
        for variant in redundant_values:
            mapping[variant] = canonical_key

    # Replace all redundant values in the specified column with the canonical key.
    df[column] = df[column].replace(mapping)
    
    print(f"Cleaned redundant entries in column '{column}'.")
    return df