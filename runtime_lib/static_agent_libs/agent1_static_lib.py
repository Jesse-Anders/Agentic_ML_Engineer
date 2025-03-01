# No unreviewed generated code is contained in this file

from word2number import w2n
from collections import Counter
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
import json
import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Shared State Getters
from utils import get_dataframe_stage, get_shared_var

# ============================================================================================#
# region                   Evaluate for Drop Null Heavy Column                                #
#=============================================================================================#

def evaluate_column_for_drop(df, drop_null_threshold=0.5, target_corr_threshold=0.3):
    """
    Evaluates a column for potential dropping based on its missingness and data relationships.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The column to evaluate.
        target (str, optional): The target column name for assessing whether missingness is predictive.
        drop_null_threshold (float): The threshold proportion (0-1) of missing values among non-null rows
                                     above which the column is considered for dropping.
        target_corr_threshold (float): If target is provided, the minimum absolute correlation between the 
                                       missingness indicator and target needed to override a high null rate.
    
    Returns:
        dict: A dictionary containing:
            - 'total_count': Total number of rows.
            - 'non_null_count': Count of non-null entries.
            - 'null_percentage': Percentage of missing values relative to non-null count.
            - 'unique_value_ratio': Ratio of unique non-null values to non-null count.
            - 'missing_target_corr': (If target provided) Correlation between missing indicator and target.
            - 'recommended_action': "drop" or "keep", with an explanation.
            - 'details': All computed metrics.
    """
    column = get_shared_var('current_column')
    target = get_shared_var('target_column')

    # Basic counts and null percentage (based on non-null entries)
    total_count = len(df)
    non_null_count = df[column].notnull().sum()
    if non_null_count == 0:
        # If there are no non-null entries, it's a clear candidate for dropping.
        return {
            "total_count": total_count,
            "non_null_count": non_null_count,
            "null_percentage": 1.0,
            "unique_value_ratio": 0,
            "recommended_action": "drop",
            "details": "Column contains only null values."
        }
    
    # Compute null percentage relative to non-null count:
    # (The logic here is: if you consider only the non-null values,
    #  what percentage is missing? In practice, you may simply use total_count,
    #  but here we subtract the missing values.)
    # Actually, if you want to consider "numeric vs. non-null", you might do:
    # null_percentage = (total_count - non_null_count) / total_count
    # But the user requested "against all entries - null entries", meaning:
    null_percentage = (total_count - non_null_count) / total_count
    
    # For additional insight, compute the unique value ratio among non-null values.
    unique_values = df[column].dropna().unique()
    unique_value_ratio = len(unique_values) / non_null_count
    
    # Initialize the dictionary of metrics.
    metrics = {
        "total_count": total_count,
        "non_null_count": non_null_count,
        "null_percentage": null_percentage,
        "unique_value_ratio": unique_value_ratio
    }
    
    # If a target column is provided, compute the correlation between the missing indicator and target.
    missing_target_corr = None
    if target is not None:
        if target not in df.columns:
            raise ValueError(f"Target column '{target}' not found in the DataFrame.")
        # Create a binary indicator for missingness in the column
        missing_indicator = df[column].isnull().astype(int)
        # Attempt to compute Pearson correlation if target is numeric.
        # (For non-numeric targets, more sophisticated methods might be needed.)
        if pd.api.types.is_numeric_dtype(df[target]):
            missing_target_corr = missing_indicator.corr(df[target])
        else:
            # For non-numeric targets, we can compute the point-biserial correlation,
            # or simply mark it as not applicable.
            missing_target_corr = np.nan
        metrics["missing_target_corr"] = missing_target_corr
    
    # Decision logic:
    # - If the null_percentage is above the threshold AND (if target provided, the absolute correlation
    #   between missingness and target is below the target_corr_threshold), recommend drop.
    # - Otherwise, recommend keep.
    if null_percentage >= drop_null_threshold:
        if target is not None and pd.notnull(missing_target_corr):
            if abs(missing_target_corr) >= target_corr_threshold:
                recommended_action = "keep"
                explanation = (f"Although {null_percentage:.2%} of rows are missing, the missingness is "
                               f"strongly correlated with the target (corr = {missing_target_corr:.2f}).")
            else:
                recommended_action = "drop"
                explanation = (f"{null_percentage:.2%} of rows are missing and missingness is not strongly correlated "
                               f"with the target (corr = {missing_target_corr:.2f}).")
        else:
            recommended_action = "drop"
            explanation = f"{null_percentage:.2%} of rows are missing; no target correlation to mitigate this."
    else:
        recommended_action = "keep"
        explanation = f"Missingness ({null_percentage:.2%}) is within acceptable limits."
    
    metrics["recommended_action"] = recommended_action
    metrics["explanation"] = explanation
    
    return metrics


def drop_column(df):
    """
    Drops a specified column from the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame from which the column will be dropped.
        column (str): The name of the column to drop.

    Returns:
        pd.DataFrame: The DataFrame with the specified column removed.
    """
    column = get_shared_var('current_column')
    
    # Ensure the column exists in the DataFrame.
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    
    # Drop the column (using inplace=False to return a new DataFrame)
    df = df.drop(columns=[column])
    print(f"Column '{column}' has been dropped from the DataFrame.")
    
    return df

#=============================================================================================#
#  region              COLUMN NUM AND ALIAS NULL CHECKERES                                #
#=============================================================================================#

def check_percent_numeric(df, numeric_threshold=0.9):
    """
    Checks whether a column is text/object or if it is 90%+ numeric,
    providing a comment on its classification.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to check.
        column (str): The name of the column to analyze.
        numeric_threshold (float): The threshold for numeric data classification (default: 0.9).

    Returns:
        str: A comment describing whether the column is text/object or numeric.
    """
    column = get_shared_var('current_column')

    # Ensure the column exists
    if column not in df.columns:
        return f"Column '{column}' does not exist in the DataFrame."

    def is_numeric(value):
        """
        Helper function to check if a value is numeric or can be safely cast to a number.
        """
        try:
            float(value)  # Try converting to a float
            return True
        except (ValueError, TypeError):
            return False

    # Count numeric and non-numeric entries
    numeric_count = df[column].apply(is_numeric).sum()
    total_exluding_nulls_count = df[column].notnull().sum()  # Total length of column excluding nulls
    numeric_ratio = numeric_count / total_exluding_nulls_count if total_exluding_nulls_count > 0 else 0

    # Determine classification
    if numeric_ratio >= numeric_threshold:
        return f"Column '{column}' is 90%+ numeric and can be considered truly numeric (Numeric Ratio: {numeric_ratio:.2%})."
    else:
        return f"Column '{column}' is less than 90% numeric and should be treated as text/object (Numeric Ratio: {numeric_ratio:.2%})."


def check_for_text_nums(df):
    """
    Checks if a column contains text entries that could represent written numbers.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to check.
        column (str): The name of the column to analyze.

    Returns:
        bool: True if the column contains text that could represent written numbers, False otherwise.
    """
    column = get_shared_var('current_column')

    # Ensure the column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    # Check for potential text numbers
    for value in df[column]:
        if isinstance(value, str):
            try:
                # Attempt to parse the text as a number
                w2n.word_to_num(value)
                return True  # Found at least one convertible text number
            except (ValueError, TypeError):
                continue

    return False  # No text numbers found

# PLEASE UPDATE TO INCLUDE LIST OF UPDATEDED/CONVERTED ENTRIES TO NUMBERS 
def convert_text_nums_to_numeric(df):
    """
    Converts written numbers in a column to numeric values.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to process.
        column (str): The name of the column to process.

    Returns:
        pd.DataFrame: The updated DataFrame with written numbers converted.
    """
    column = get_shared_var('current_column')

    # Ensure the column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    # Convert text numbers to numeric values
    for i, value in df[column].items():
        try:
            if isinstance(value, str):
                # Convert written number to numeric
                df.at[i, column] = w2n.word_to_num(value)
        except (ValueError, TypeError):
            # Skip invalid entries
            continue

    return df



def describe_and_clean_non_numeric_entries(df):
    """
    Identifies traditional alias nulls, converts them to proper NaN values, and converts
    all remaining non-numeric (text) entries to NaN. It also returns a summary of these changes.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to process.
        column (str): The name of the column to analyze.

    Returns:
        dict: A dictionary containing:
            - 'alias_null_summary': Summary of alias nulls found and converted, including counts of each.
            - 'unique_review_list': List of non-numeric entries that were found and converted.
    """
    column = get_shared_var('current_column')

    # Ensure the column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    def is_non_numeric(value):
        """
        Helper function to determine if a value is non-numeric.
        Numeric-like strings (e.g., '23') are treated as numeric.
        """
        if pd.isna(value):  # Treat NaNs as numeric
            return False
        try:
            float(value)  # Attempt to cast to float
            return False  # If successful, it's numeric-like
        except (ValueError, TypeError):
            return True  # Otherwise, it's non-numeric

    # Define traditional alias nulls
    alias_nulls = {"na", "n/a", "null", "missing", "none", "nan", "not available", "unknown", "empty", "no data", "data missing"}

    # Normalize the column for processing
    normalized_column = df[column].apply(lambda x: x.strip().lower() if isinstance(x, str) else x)

    # Count and convert alias nulls to NaN
    alias_null_counts = Counter(normalized_column[normalized_column.isin(alias_nulls)])
    df.loc[normalized_column.isin(alias_nulls), column] = pd.NA

    # Identify non-numeric entries that are not alias nulls
    non_numeric_entries = normalized_column[normalized_column.apply(is_non_numeric) & ~normalized_column.isin(alias_nulls)]

    # List and count of unique non-numeric entries that are not alias nulls
    unique_non_numeric_entries = non_numeric_entries.unique()

    # Convert all non-numeric entries to NaN
    df.loc[non_numeric_entries.index, column] = pd.NA

    # Generate detailed output
    alias_null_summary = ", ".join([f"{key}: {value}" for key, value in alias_null_counts.items()])
    alias_null_count_total = sum(alias_null_counts.values())
    unique_review_list = list(unique_non_numeric_entries)

    # Return detailed information
    return {
        "alias_null_summary": f"Converted {alias_null_count_total} alias nulls to proper NaN. {alias_null_summary}",
        "unique_review_list": f"{len(unique_review_list)} unique non-numeric entries were found and converted to NaN: {unique_review_list}"
    }


def convert_column_to_numeric(df):
    """
    Converts the column to numeric (either int or float) based on the data.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to convert.
        column (str): The name of the column to convert.

    Returns:
        pd.DataFrame: The DataFrame with the converted column.
    """
    column = get_shared_var('current_column')

    # Ensure the column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    
    # Try converting the column to integer if possible
    df[column] = pd.to_numeric(df[column], errors='coerce', downcast='integer')
    
    # If the conversion to integer fails (e.g., due to decimals or NaNs), convert to float
    if not pd.api.types.is_integer_dtype(df[column]):
        df[column] = pd.to_numeric(df[column], errors='coerce', downcast='float')

    return df


# This is applied to regular Object Columns
def convert_common_alias_nulls(df):
    """
    Converts common alias null values in a text column to proper NaN values,
    and prints a summary of how many of each alias null were found and converted.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to process.
        column (str): The name of the column to convert.

    Returns:
        pd.DataFrame: The DataFrame with the specified column updated.
    """
    column = get_shared_var('current_column')

    # Ensure the column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    # Define traditional alias nulls
    alias_nulls = {"na", "n/a", "null", "missing", "none", "nan", "not available", "unknown", "empty", "no data", "data missing"}

    # Normalize the column for processing
    normalized_column = df[column].apply(lambda x: str(x).strip().lower() if isinstance(x, str) else x)

    # Count the occurrences of alias nulls
    alias_null_counts = Counter(normalized_column[normalized_column.isin(alias_nulls)])

    # Print a summary of alias null counts
    if alias_null_counts:
        print("Alias Nulls Summary:")
        for alias, count in alias_null_counts.items():
            print(f"  {alias}: {count}")
    else:
        print("No alias nulls found.")

    # Replace alias nulls with NaN
    df.loc[normalized_column.isin(alias_nulls), column] = pd.NA

    return df


def display_most_common_unique_entries(df, max_display=40):
    """
    Displays the most common unique entries in a column, limited to the top `max_display` most common entries.
    It only shows the entries without counts.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to process.
        column (str): The name of the column to analyze.
        max_display (int): The maximum number of unique entries to display (default is 40).

    Returns:
        list: A list of the top unique entries (without counts), up to `max_display` entries.
    """
    column = get_shared_var('current_column')

    # Ensure the column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    
    # Get the value counts for the column, sorted by count in descending order
    value_counts = df[column].value_counts()

    # Limit to the top 'max_display' entries
    top_entries = value_counts.head(max_display).index.tolist()

    return top_entries
    


def convert_uncommon_alias_nulls(df, json_path="json_lib/alias_nulls_list.json"):
    """
    Converts all alias null values stored in the JSON file to proper NaN values in the specified column of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to process.
        column (str): The name of the column to convert.
        json_path (str): The path to the JSON file containing the alias nulls list (default is "json_lib/alias_nulls_list.json").

    Returns:
        pd.DataFrame: The updated DataFrame with the alias nulls converted to NaN.
    """
    column = get_shared_var('current_column')
    
    # Ensure the column exists in the DataFrame
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    try:
        # Load the list of alias nulls from the JSON file
        with open(json_path, "r") as file:
            alias_nulls = json.load(file)

        # Normalize the list of alias nulls (convert to lowercase for consistent matching)
        alias_nulls = [item.strip().lower() for item in alias_nulls]

        # Normalize the column for processing
        normalized_column = df[column].apply(lambda x: str(x).strip().lower() if isinstance(x, str) else x)

        # Replace alias nulls with NaN
        df.loc[normalized_column.isin(alias_nulls), column] = pd.NA
        print(f"Converted {alias_nulls} to proper null data type")

        # After using alias_nulls, clear the JSON file
        with open(json_path, "w") as file:
        json.dump([], file)  # Empty object

        return df

    except FileNotFoundError:
        raise FileNotFoundError(f"Alias nulls file not found at {json_path}.")
    except json.JSONDecodeError:
        raise ValueError(f"Error: Nulls list file at {json_path} is not a valid JSON file.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")