# No unreviewed generated code is contained in this file

# Every function should ideally have a [description]: field within its docstring

from word2number import w2n
from collections import Counter
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
import json


def drop_df_duplicates(df):
    '''
    [description]: Drops duplicate rows from a DataFrame "in place"
    '''
    start_rows = len(df)
    df.drop_duplicates(inplace=True)
    end_rows = len(df)

    return f'Dropped {start_rows - end_rows} duplicate rows. There are {end_rows} remaining rows.'


#=============================================================================================#
#  region              COLUMN NUM AND ALIAS NULL CHECKERES                                #
#=============================================================================================#


def check_percent_numeric(df, column, numeric_threshold=0.9):
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
    total_count = len(df[column])
    numeric_ratio = numeric_count / total_count if total_count > 0 else 0

    # Determine classification
    if numeric_ratio >= numeric_threshold:
        return f"Column '{column}' is 90%+ numeric and can be considered truly numeric (Numeric Ratio: {numeric_ratio:.2%})."
    else:
        return f"Column '{column}' is less than 90% numeric and should be treated as text/object (Numeric Ratio: {numeric_ratio:.2%})."

def check_for_text_nums(df, column):
    """
    Checks if a column contains text entries that could represent written numbers.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to check.
        column (str): The name of the column to analyze.

    Returns:
        bool: True if the column contains text that could represent written numbers, False otherwise.
    """
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
def convert_text_nums_to_numeric(df, column):
    """
    Converts written numbers in a column to numeric values.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to process.
        column (str): The name of the column to process.

    Returns:
        pd.DataFrame: The updated DataFrame with written numbers converted.
    """
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



def describe_and_clean_non_numeric_entries(df, column):
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


def convert_column_to_numeric(df, column):
    """
    Converts the column to numeric (either int or float) based on the data.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to convert.
        column (str): The name of the column to convert.

    Returns:
        pd.DataFrame: The DataFrame with the converted column.
    """
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
def convert_common_alias_nulls(df, column):
    """
    Converts common alias null values in a text column to proper NaN values,
    and prints a summary of how many of each alias null were found and converted.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to process.
        column (str): The name of the column to convert.

    Returns:
        pd.DataFrame: The DataFrame with the specified column updated.
    """
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


def display_most_common_unique_entries(df, column, max_display=40):
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
    # Ensure the column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    
    # Get the value counts for the column, sorted by count in descending order
    value_counts = df[column].value_counts()

    # Limit to the top 'max_display' entries
    top_entries = value_counts.head(max_display).index.tolist()

    return top_entries

def convert_uncommon_alias_nulls(df, column, alias_nulls_path="json_lib/alias_nulls_list.json"):
    """
    Converts all alias null values stored in the JSON file to proper NaN values in the specified column of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to process.
        column (str): The name of the column to convert.
        alias_nulls_path (str): The path to the JSON file containing the alias nulls list (default is "json_lib/alias_nulls_list.json").

    Returns:
        pd.DataFrame: The updated DataFrame with the alias nulls converted to NaN.
    """
    # Ensure the column exists in the DataFrame
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    try:
        # Load the list of alias nulls from the JSON file
        with open(alias_nulls_path, "r") as file:
            alias_nulls = json.load(file)

        # Normalize the list of alias nulls (convert to lowercase for consistent matching)
        alias_nulls = [item.strip().lower() for item in alias_nulls]

        # Normalize the column for processing
        normalized_column = df[column].apply(lambda x: str(x).strip().lower() if isinstance(x, str) else x)

        # Replace alias nulls with NaN
        df.loc[normalized_column.isin(alias_nulls), column] = pd.NA
        print(f"Converted {alias_nulls} to proper null data type")

        return df

    except FileNotFoundError:
        raise FileNotFoundError(f"Alias nulls file not found at {alias_nulls_path}.")
    except json.JSONDecodeError:
        raise ValueError(f"Error: Nulls list file at {alias_nulls_path} is not a valid JSON file.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


#=============================================================================================#
#  region              COLUMN START - Determine Data Type                                     #
#=============================================================================================#

def data_type_check(df, column) -> str:
    """
    Checks the data type of the given column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame.
        column (str): The name of the column to check.

    Returns:
        str: A message describing the column's data type.
    """
    column_dtype = df[column].dtype # Access the column dynamically

    # Handle text data
    if column_dtype == 'object':
        return f"Column '{column}' contains text data (dtype: {column_dtype})."
    
    # Handle integer data
    elif column_dtype == 'int64':
        return f"Column '{column}' contains integer data (dtype: {column_dtype})."
    
    # Handle float data
    elif column_dtype == 'float64':
        return f"Column '{column}' contains floating-point data (dtype: {column_dtype})."
    
    # Handle boolean data
    elif column_dtype == 'bool':
        return f"Column '{column}' contains boolean data (dtype: {column_dtype})."
    
    # Handle datetime data
    elif column_dtype == 'datetime64[ns]':
        return f"Column '{column}' contains datetime data (dtype: {column_dtype})."
    
    # Handle categorical data
    elif pd.api.types.is_categorical_dtype(df[column]):
        return f"Column '{column}' contains categorical data (dtype: {column_dtype})."
    
    # Handle other unhandled data types
    else:
        return f"Column '{column}' has an unhandled data type: {column_dtype}."
    

#=============================================================================================#
#  region              INTEGER & FLOAT Column Functions                                       #
#=============================================================================================#
def determine_numeric_or_categorical(df, column, numeric_override_threshold=0.9):
    """
    Identifies whether an integer column is numeric or categorical.
    Overrides classification if data is truly numeric despite skewed unique ratios.

    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column (str): The name of the column to analyze.
        numeric_override_threshold (float): The proportion of non-dominant unique values to classify as numeric.

    Returns:
        dict: A dictionary containing the column type, handling strategy, and the updated DataFrame.
    """

    # Ensure the column exists and is of integer type
    if column not in df.columns:
        return {"error": f"Column '{column}' does not exist in the DataFrame."}

    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error": f"Column '{column}' is not of integer data type."}
    

    # Count unique values and their frequencies
    unique_values = df[column].value_counts(normalize=True)  # Frequencies as proportions
    dominant_value_ratio = unique_values.iloc[0]  # Proportion of the most frequent value

    # Analyze the unique-to-total ratio
    unique_count = df[column].nunique()
    total_count = len(df[column])
    unique_ratio = unique_count / total_count

    # Determine if data is numeric or categorical
    # Override to numeric if most values are unique despite dominant values
    if unique_ratio > 0.05 or unique_values.iloc[1:].sum() > numeric_override_threshold:
        column_type = "numeric"
    else:
        column_type = "categorical"

    return {
        "column": column,
        "column_type": column_type,
        # "null_count": df[column].isnull().sum(),  # Log null values
        # "unique_ratio": unique_ratio,
        # "dominant_value_ratio": dominant_value_ratio,
        # "handling_strategy": handling_strategy,
        # "updated_df": df,
    }
    #=============================================================================#
    #  region              INTEGER & FLOAT Column NUMERIC Functions               #
    #=============================================================================#
def check_outliers_and_nulls(df, column):
    """
    Checks for outliers in a column with an integer data type using the IQR method.
    Explicitly handles null values by removing them before calculations.

    Args:
        df (pd.DataFrame): The DataFrame containing the column to check.
        column (str): The name of the column to analyze.

    Returns:
        dict: A dictionary containing the outliers and basic statistics.
    """
    # Ensure the column exists and is of integer type
    if column not in df.columns:
        return {"error": f"Column '{column}' does not exist in the DataFrame."}
    
    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error": f"Column '{column}' is not of integer data type."}

    # Drop null values from the column
    col_data = df[column].dropna()

    # Compute basic statistics
    q1 = col_data.quantile(0.25)  # First quartile (25th percentile)
    q3 = col_data.quantile(0.75)  # Third quartile (75th percentile)
    iqr = q3 - q1                 # Interquartile range

    # Define outlier thresholds
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Identify outliers
    outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]

    # Return results
    return {
        "column": column,
        #"lower_bound": lower_bound,
        #"upper_bound": upper_bound,
        #"outliers": outliers.tolist(),
        "outlier_count": len(outliers),
        #"q1": q1,
        #"q3": q3,
        #"iqr": iqr,
        "null_count": df[column].isnull().sum(),  # Log null values
    }


def cap_outliers_and_impute_nulls(df, column):
    """
    Caps outliers to the 95th and 5th percentiles (Winsorizing) and imputes nulls with the median value.
    Maintains the column's original data type, rounding to the nearest integer for integers
    or to the appropriate precision for floats.

    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column (str): The name of the column to process.

    Returns:
        pd.DataFrame: The updated DataFrame with outliers capped and nulls imputed.
    """
    # Skip non-numeric columns
    if not pd.api.types.is_numeric_dtype(df[column]):
        print(f"Skipped non-numeric column: {column}")
        return df

    # Exclude nulls from calculations
    non_null_values = df[column].dropna()

    # Cap Outliers (Winsorizing)
    # Calculate the 5th and 95th percentiles of the column (excluding nulls)
    percentile_5 = non_null_values.quantile(0.05)
    percentile_95 = non_null_values.quantile(0.95)

    # Count values to be replaced
    count_below_5 = np.sum(non_null_values < percentile_5)
    count_above_95 = np.sum(non_null_values > percentile_95)

    # Handle rounding based on column type
    if pd.api.types.is_integer_dtype(df[column]):
        # Integer columns: Round to the nearest integer
        percentile_5 = round(percentile_5)
        percentile_95 = round(percentile_95)
        round_func = lambda x: round(x)
    else:
        # Float columns: Determine maximum precision (decimal places deep) currently existing in column and rounds accordingly
        max_precision = non_null_values.apply(lambda x: len(str(x).split(".")[1]) if "." in str(x) else 0).max()
        round_func = lambda x: round(x, max_precision)

    # Replace values less than the 5th percentile with the 5th percentile
    df.loc[df[column] < percentile_5, column] = round_func(percentile_5)

    # Replace values greater than the 95th percentile with the 95th percentile
    df.loc[df[column] > percentile_95, column] = round_func(percentile_95)

    # Print replaced counts and values
    if count_below_5 > 0:
        print(f"Column '{column}': Replaced {count_below_5} values with {round_func(percentile_5)} (5th percentile).")
    if count_above_95 > 0:
        print(f"Column '{column}': Replaced {count_above_95} values with {round_func(percentile_95)} (95th percentile).")
    if count_below_5 == 0 and count_above_95 == 0:
        print(f"Skipped no outliers in column: {column}")

    # Impute Nulls
    if df[column].isnull().sum() > 0:
        median_value = round_func(non_null_values.median())
        null_count = df[column].isnull().sum()
        # df[column].fillna(median_value, inplace=True) # Replaced with recommend for Pandas 3.0 in next line
        df.fillna({column: median_value}, inplace=True)

        print(f"Column '{column}': Imputed {null_count} null values with median value {median_value}.")
    else:
        print(f"Column '{column}': No nulls to impute.")

    return df


# endregion
    #=============================================================================#
    #  region              NUMERIC Column CATEGORICAL Functions                   #
    #=============================================================================#
# Import Categorical Nulls as Mode or Create Unique ex_null Category
def impute_mode_or_create_exnulls_cat(df, column):
    # Skip columns that are not of type 'object'
    if df[column].dtype != 'object':
        print(f"Skipped is not of type 'object':{column}")
        return df

    # Proceed with columns of type 'object'
    total_items = len(df[column])
    null_count = df[column].isnull().sum()

    # Early exit if no nulls
    if null_count == 0:
        print(f"Skipped No Nulls in: {column}: ")
        return df

    # Calculate statistics
    value_counts = df[column].value_counts()  # Excludes nulls automatically
    min_cat_count = value_counts.min()
    max_cat_count = value_counts.max()
    max_cat_percent = max_cat_count / total_items
    null_cat_percent = null_count / total_items

    # Determine the mode; mode can return multiple values, so ensure to get the first one if that's the case
    mode = df[column].mode().iloc[0]

    # Impute Nulls as ex_null If they represent more than 5% of Column 
    # And they have at least as many values as the smallest category
    # And the Mode category is not over 80%
    # AUGMENTED TO 1% FOR JOBS DATA SET (SET BACK TO 5%)
    
    if null_count >= min_cat_count and null_cat_percent >= 0.01 and max_cat_percent < 0.8:
        fill_value = 'ex_null'
        print(f"{column}: {null_count} nulls imputed as 'ex_null'")
    else:
        fill_value = mode
        print(f"{column}: {null_count} nulls imputed as '{mode}', the Mode value")

    df[column].fillna(fill_value, inplace=True)

    return df

# Example usage
# Assuming 'df' is your DataFrame and 'category_feature' is the column you want to process
# df = impute_or_convert_nulls(df, 'category_feature')


# endregion
# endregion
#=============================================================================================#
#  region              FLOAT Column Functions                                                 #
#=============================================================================================#
def if_float_is_really_int_convert(df, column):
    """
    Checks if a column with a float data type contains only values ending in .0
    and converts it to an integer data type if true.

    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column (str): The name of the column to check and possibly convert.

    Returns:
        pd.DataFrame: The updated DataFrame with the column converted if applicable.
        str: A message indicating whether the column was converted or not.
    """
    # Ensure the column exists and is of float type
    if column not in df.columns:
        return df, f"Column '{column}' does not exist in the DataFrame."
    
    if not pd.api.types.is_float_dtype(df[column]):
        return df, f"Column '{column}' is not of float data type."

    # Check if all values are integers (when ignoring nulls)
    non_null_values = df[column].dropna()  # Exclude null values
    if (non_null_values % 1 == 0).all():  # Check if all values are whole numbers
        df[column] = df[column].astype("Int64")  # Use pandas nullable integer type
        return df, f"Column '{column}' has been converted to integer."
    else:
        return df, f"Column '{column}' remains as float."

    #=============================================================================#
    #  region              FLOAT Column NUMERIC Functions                         #
    #=============================================================================#

# endregion
    #=============================================================================#
    #  region              FLOAT Column CATEGORICAL Functions                     #
    #=============================================================================#

#endregion
# endregion