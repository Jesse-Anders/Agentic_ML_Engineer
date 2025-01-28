# No unreviewed generated code is contained in this file

# Every function should ideally have a [description]: field within its docstring

from text2num import text2num
import pandas as pd
import numpy as np

def drop_df_duplicates(df):
    '''
    [description]: Drops duplicate rows from a DataFrame "in place"
    '''
    start_rows = len(df)
    df.drop_duplicates(inplace=True)
    end_rows = len(df)

    return f'Dropped {start_rows - end_rows} duplicate rows. There are {end_rows} remaining rows.'


#=============================================================================================#
#  region              COLUMN UNIVERSALS - Determine Data Type                                #
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

    # Count numeric and non-numeric entries
    numeric_count = df[column].apply(lambda x: isinstance(x, (int, float)) or pd.api.types.is_number(x)).sum()
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
                text2num(value)
                return True  # Found at least one convertible text number
            except (ValueError, TypeError):
                continue

    return False  # No text numbers found

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
                df.at[i, column] = text2num(value)
        except (ValueError, TypeError):
            # Skip invalid entries
            continue

    return df


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
    Caps outliers to the 95th and 5th percentiles (Winsorizing) and imputes nulls with the mean value.
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
        mean_value = round_func(non_null_values.mean())
        null_count = df[column].isnull().sum()
        # df[column].fillna(mean_value, inplace=True) # Replaced with recommend for Pandas 3.0 in next line
        df.fillna({column: mean_value}, inplace=True)

        print(f"Column '{column}': Imputed {null_count} null values with mean value {mean_value}.")
    else:
        print(f"Column '{column}': No nulls to impute.")

    return df


# endregion
    #=============================================================================#
    #  region              INTEGER Column CATEGORICAL Functions                   #
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