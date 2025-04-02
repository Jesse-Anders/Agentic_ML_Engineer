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
    # Retrieve the redundancy dictionary from shared memory
    redundancy_dictionary = get_shared_var('redundancy_dictionary')
    
    # If no dictionary is found, do not proceed
    if not redundancy_dictionary:
        return "No redundancy dictionary found in shared state."

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the dictionary to the JSON file
    with open(file_path, 'w') as file:
        json.dump(redundancy_dictionary, file, indent=4)

    return f"Redundancy dictionary saved to {file_path}"


import os
import json

def display_redundancy_json(file_path='json_lib/saved_redundancy_dictionary.json'):
    """
    Reads and returns the contents of the saved redundancy dictionary JSON file 
    as a formatted string for display purposes.
    
    Args:
        file_path (str): Path to the JSON file. Defaults to 'json_lib/saved_redundancy_dictionary.json'.
        
    Returns:
        str: Formatted contents of the JSON file, or an error message if the file doesn't exist or an error occurs.
    """
    # Convert to an absolute path to avoid issues with relative paths
    abs_file_path = os.path.abspath(file_path)
    
    if not os.path.exists(abs_file_path):
        return f"No file found at {abs_file_path}."
    
    try:
        with open(abs_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        return f"Error reading file: {e}"
    
    formatted_json = json.dumps(data, indent=4)
    
    # Optionally print to ensure the output is displayed in the workflow
    print(formatted_json)
    
    return formatted_json


def clean_redundant_entries(df, file_path='json_lib/saved_redundancy_dictionary.json'):
    """
    Cleans redundant entries in the DataFrame by replacing variant values with their canonical versions.
    
    The function expects a JSON file at the given file_path in the following format:
    
    {
        "column_name": {
            "canonical_value": ["variant1", "variant2", ...],
            ...
        },
        ...
    }
    
    For each column in the JSON that exists in df, each variant found in the list
    will be replaced by the canonical value.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to be cleaned.
        file_path (str): Path to the JSON redundancy dictionary file.
        
    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    # Load the redundancy mapping dictionary from the JSON file
    with open(file_path, 'r') as f:
        mapping_data = json.load(f)
    
    # Loop over each column mapping from the JSON file
    for column, mappings in mapping_data.items():
        if column in df.columns:
            # Build a dictionary where each variant maps to its canonical value
            replacement_dict = {}
            for canonical_value, variants in mappings.items():
                for variant in variants:
                    replacement_dict[variant] = canonical_value
            # Replace the variant values in the DataFrame column
            df[column] = df[column].replace(replacement_dict)
    
    return df
