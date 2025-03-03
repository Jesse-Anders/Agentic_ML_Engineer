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

def clean_redundant_entries(df):
    """
    Cleans redundant entries in a specified DataFrame column by mapping them to their canonical key.
    
    The function retrieves the column-specific redundancy dictionary from shared variables (under the key
    'redundancy_dictionary') and the current column name via get_shared_var('current_column'). It then constructs
    a mapping from each redundant variant to its canonical key and applies this mapping to update the column values.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the column to be cleaned.
        
    Returns:
        pd.DataFrame: The updated DataFrame with redundant entries replaced by their canonical key.
    """
    # Retrieve the current column and redundancy dictionary from shared variables
    column = get_shared_var('current_column')
    redundancy_dict = get_shared_var('redundancy_dictionary')

    # If no dictionary is found or there's no entry for the current column, do nothing
    if redundancy_dict is None or column not in redundancy_dict:
        print("No redundancy dictionary found for current column. No changes applied.")
        return df
    
    # Build the mapping dictionary: for each canonical key in the current column's dictionary,
    # map each redundant variant to its canonical key.
    mapping = {}
    for canonical_key, redundant_values in redundancy_dict[column].items():
        for variant in redundant_values:
            mapping[variant] = canonical_key

    # Replace all redundant values in the specified column with the canonical key.
    df[column] = df[column].replace(mapping)
    
    print(f"Cleaned redundant entries in column '{column}'.")
    return df
