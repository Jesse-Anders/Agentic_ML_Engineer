from word2number import w2n
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


#=============================================================================================#
#  region              DETERMINE COLUMN DATA TYPE                                             #
#=============================================================================================#

def data_type_check(df) -> str:
    """
    Checks the data type of the given column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame.
        column (str): The name of the column to check.

    Returns:
        str: A message describing the column's data type.
    """
    column=get_shared_var('current_column')

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
    
# endregion

#=============================================================================================#
#  region              CHECK FOR BOOLEAN & CONVERT ALL BOOLEAN TO 1/0                         #
#=============================================================================================#

def check_for_bool(df):
    """
    Determines if a column contains boolean-type entries at least 95% of the time 
    (excluding nulls). The valid boolean indicators (case-insensitive) are:
    'true', 'false', 't', 'f'.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the column.
    column : str
        The name of the column to check.

    Returns
    -------
    str
        A message indicating whether the column is or is not considered boolean.
    """
    column=get_shared_var('current_column')

    if column not in df.columns:
        return f"Column '{column}' does not exist in the DataFrame."

    # Drop nulls, convert to lowercase strings
    col_data = df[column].dropna().astype(str).str.lower()

    # If there are no non-null values, we can't determine
    if len(col_data) == 0:
        return f"Cannot determine bool type for '{column}' (no non-null data)."

    # Define the allowed set of boolean strings
    allowed_booleans = {"true", "false", "t", "f"}

    # Count how many entries are in the allowed set
    bool_count = col_data.isin(allowed_booleans).sum()

    # Calculate the ratio of valid boolean-like entries
    total_count = len(col_data)
    bool_ratio = bool_count / total_count

    # If at least 95% of values are boolean-like, classify as boolean
    if bool_ratio >= 0.95:
        return f"'{column}' is a boolean type (valid boolean ratio = {bool_ratio:.2f})."
    else:
        return f"'{column}' is not a boolean type (valid boolean ratio = {bool_ratio:.2f})."
    
def encode_bool_to_num_cat(df):
    """
    Encodes a single column's True/False (or T/F) values to numeric 1/0.

    The column name is retrieved from get_shared_var('current_column').
    - If the column has dtype=bool, True -> 1, False -> 0.
    - If it's an object/string column, and all non-null values are among
      {'true','false','t','f'} (case-insensitive), map them to 1/0.
    - Otherwise, leave the column as-is.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to modify.

    Returns
    -------
    pd.DataFrame
        The updated DataFrame with boolean-like column mapped to 1/0 (if applicable).
    """
    column = get_shared_var('current_column')

    if column not in df.columns:
        print(f"Column '{column}' not found in DataFrame. Skipping...")
        return df  # No change
    
    col_dtype = df[column].dtype
    allowed_booleans = {"true", "false", "t", "f"}

    # If it's a native boolean column:
    if col_dtype == bool:
        df[column] = df[column].astype(int)  # True->1, False->0
        print(f"Converted native bool column '{column}' to 1/0.")
        return df

    # Otherwise, if it's an object/string column:
    if col_dtype == object or str(col_dtype) == "string":
        col_lower = df[column].dropna().astype(str).str.lower()
        unique_vals = set(col_lower.unique())

        # Check if all non-null values are in the allowed set
        if unique_vals.issubset(allowed_booleans):
            mapping = {"true": 1, "t": 1, "false": 0, "f": 0}
            df[column] = col_lower.map(mapping)
            
            # Convert to integer type - consider "Int64" if you want to keep nulls
            df[column] = df[column].astype(float).astype("Int64")
            print(f"Converted string column '{column}' to 1/0 for T/F values.")
        else:
            print((f"Column '{column}' not a valid boolean string column. "
                   f"Contains other values: {unique_vals}. No change made."))

    return df


#=============================================================================================#
#  region              CONVERT FLOAT TO INTEGER IF POSSIBLE                                   #
#=============================================================================================#
def if_float_is_really_int_convert(df):
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
    column=get_shared_var('current_column')

    # Ensure the column exists and is of float type
    if column not in df.columns:
        return df, f"Column '{column}' does not exist in the DataFrame."
    
    if not pd.api.types.is_float_dtype(df[column]):
        return df, f"Column '{column}' is not of float data type."

    # Check if all values are integers (when ignoring nulls)
    non_null_values = df[column].dropna()  # Exclude null values
    if (non_null_values % 1 == 0).all():  # Check if all values are whole numbers
        df[column] = df[column].astype("Int64")  # Use pandas nullable integer type
        # return df, f"Column '{column}' has been converted to integer." # cannot return additional values along with df
        return df
    else:
        # return df, f"Column '{column}' remains as float." # cannot return additional values along with df
        return df

# endregion
#=============================================================================================#
#  region              DETERMINE NUMERIC OR CATEGORICAL                                       #
#=============================================================================================#
def determine_numeric_or_categorical(df, numeric_override_threshold=0.9):
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
    column=get_shared_var('current_column')

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
# endregion
# ============================================================================================#
# region               OUTLIER HANDLING                                                       #
#=============================================================================================#

def evaluate_outliers(df, iqr_multiplier=1.5):
    """
    Evaluates a numeric column to assess the presence and severity of outliers.
    
    Computes the Q1, Q3, IQR, and percentage of values outside the [Q1 - iqr_multiplier * IQR, Q3 + iqr_multiplier * IQR] range.
    Based on these statistics, recommends a handling strategy.
    
    Args:
        df (pd.DataFrame): DataFrame containing the column.
        column (str): The name of the numeric column.
        iqr_multiplier (float): Multiplier for the IQR to define outlier boundaries (default is 1.5).
    
    Returns:
        dict: A dictionary with the following keys:
            - q1: First quartile.
            - q3: Third quartile.
            - iqr: Interquartile range.
            - lower_bound: Lower cutoff.
            - upper_bound: Upper cutoff.
            - outlier_percentage: Proportion of values outside the cutoff.
            - recommended_action: Recommendation string (e.g., "remove", "winsorize", "transform", "keep").
    """
    column=get_shared_var('current_column')

    # Drop nulls for computation
    data = df[column].dropna()
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    
    lower_bound = q1 - iqr_multiplier * iqr
    upper_bound = q3 + iqr_multiplier * iqr
    
    # Count outliers
    outliers = data[(data < lower_bound) | (data > upper_bound)]
    outlier_percentage = len(outliers) / len(data) if len(data) > 0 else 0

    # Make a recommendation:
    #   - If <5% outliers: "keep" (or minimal action needed)
    #   - If 5-15%: "winsorize" might be sufficient
    #   - If >15%: consider "transform" or further investigation; removal may be warranted if feature is unreliable.
    if outlier_percentage < 0.05:
        recommended_action = "keep"
    elif outlier_percentage < 0.15:
        recommended_action = "winsorize"
    else:
        recommended_action = "transform"

    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outlier_percentage": outlier_percentage,
        "recommended_action": recommended_action
    }

def winsorize_column(df, iqr_multiplier=1.5):
    """
    Applies winsorization to a numeric column, capping values at the lower and upper bounds defined by IQR.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column (str): The numeric column to winsorize.
        iqr_multiplier (float): Multiplier for the IQR to define outlier bounds.
    
    Returns:
        pd.DataFrame: DataFrame with the specified column winsorized.
    """
    column=get_shared_var('current_column')

    # Compute bounds from non-null values
    data = df[column].dropna()
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - iqr_multiplier * iqr
    upper_bound = q3 + iqr_multiplier * iqr
    
    # Winsorize: cap values outside the bounds
    df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
    print(f"Column '{column}' winsorized with bounds: [{lower_bound}, {upper_bound}].")
    return df

def log_transform_column(df):
    """
    Applies a log transformation to a numeric column. 
    Assumes all values are positive; if not, shifts the column so that all values are positive.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column (str): The numeric column to transform.
    
    Returns:
        pd.DataFrame: DataFrame with the column log-transformed.
    """
    column=get_shared_var('current_column')

    # Check if any value is <= 0
    if (df[column] <= 0).any():
        # Shift by the absolute minimum + a small constant to avoid log(0)
        shift = abs(df[column].min()) + 1e-6
        print(f"Shifting column '{column}' by {shift} to ensure positivity for log transform.")
        df[column] = df[column] + shift
    
    df[column] = np.log(df[column])
    print(f"Column '{column}' log-transformed.")
    return df

# endregion
# ============================================================================================#
#    region            NULL HANDLING CHAIN (Numeric as Numeric)                               #
#=============================================================================================#

# This def decides if numeric imputes Should be done with KNN or Stochastic Median
# It checks KNN viabilty only with features that are correlated to the current column.

# IMPORTANT! This needs to be updated to calculate KNN based on preprocessor.save_stage_df('POST_AGENT_1')
def evaluate_imputation_strategy(df, 
                                 correlation_threshold=0.3, 
                                 null_threshold=0.5, 
                                 skew_threshold=2.0, 
                                 null_skewness_threshold=1.5, 
                                 w_nulls=1.0, w_skew=0.5, 
                                 min_strong_features=2):
    """
    Evaluates correlation, percentage of nulls, and skewness of a given column to determine the imputation strategy.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The column being evaluated for imputation.
        correlation_threshold (float): Minimum absolute correlation value to consider a strong relationship.
        null_threshold (float): Proportion of missing values above which KNN may not be recommended.
        skew_threshold (float): Skewness value above which median imputation may be preferred.
        null_skewness_threshold (float): Threshold for determining when null percentage and skewness conspire against KNN.
        w_nulls (float): Weight factor for null percentage in null-skew interaction.
        w_skew (float): Weight factor for skewness in null-skew interaction.
        min_strong_features (int): Minimum number of highly correlated features required for KNN.

    Returns:
        dict: A dictionary containing:
            - 'top_correlated_features': List of numeric columns highly correlated with the target column.
            - 'num_strong_features': Count of strongly correlated features.
            - 'correlation_max': Maximum absolute correlation with other features.
            - 'highly_correlated': Boolean indicating if strong correlation exists.
            - 'percent_nulls': Percentage of missing values in the column.
            - 'high_nulls': Boolean indicating if null percentage exceeds threshold.
            - 'skewness': Skewness value of the column.
            - 'highly_skewed': Boolean indicating if skewness exceeds threshold.
            - 'null_skewness_conspire': Boolean indicating if missingness and skewness together make KNN unreliable.
            - 'recommended_imputation': The recommended imputation method ("stochastic median" or "KNN").
    """
    column=get_shared_var('current_column')

    # Ensure column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    # Ensure the column is numeric
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(f"Column '{column}' must be numeric for correlation and skew analysis.")

    # Compute percentage of nulls
    percent_nulls = df[column].isnull().mean()
    high_nulls = percent_nulls > null_threshold

    # Compute correlation with other numeric features
    numeric_features = df.select_dtypes(include=[np.number]).columns.drop(column, errors='ignore')

    if len(numeric_features) > 0:
        correlation_series = df[numeric_features].corrwith(df[column], method='pearson')

        # Filter features with meaningful correlation
        strong_correlated_features = correlation_series[correlation_series.abs() >= correlation_threshold].index.tolist()
        num_strong_features = len(strong_correlated_features)

        # Get max correlation value
        correlation_max = correlation_series.abs().max()
        highly_correlated = num_strong_features >= min_strong_features
    else:
        correlation_max = 0
        highly_correlated = False
        strong_correlated_features = []
        num_strong_features = 0

    # Compute skewness
    skewness = df[column].skew()
    highly_skewed = abs(skewness) > skew_threshold

    # Compute null-skewness interaction
    null_skewness_score = (percent_nulls * w_nulls) + (abs(skewness) * w_skew)
    null_skewness_conspire = null_skewness_score > null_skewness_threshold

    # Decision Logic for Imputation Strategy
    if not highly_correlated:
        recommended_imputation = "stochastic median"
    elif high_nulls or highly_skewed or null_skewness_conspire:
        recommended_imputation = "stochastic median"
    else:
        recommended_imputation = "KNN"

    # Return the evaluation results
    return {
        "top_correlated_features": strong_correlated_features,
        "num_strong_features": num_strong_features,
        "correlation_max": correlation_max,
        "highly_correlated": highly_correlated,
        "percent_nulls": percent_nulls,
        "high_nulls": high_nulls,
        "skewness": skewness,
        "highly_skewed": highly_skewed,
        "null_skewness_conspire": null_skewness_conspire,
        "recommended_imputation": recommended_imputation
    }

# This needs to be updated to calculate KNN based on preprocessor.save_stage_df('POST_AGENT_1')
# BUT MUST SAVE CHANGES TO MAIN DF!!!
def knn_impute_with_rounding(df,
                             correlation_threshold=0.3, 
                             min_strong_features=2, 
                             n_neighbors=5):
    """
    Performs KNN imputation on a numeric column using only strongly correlated features.
    Ensures that imputed values maintain the same decimal precision as existing values.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The column with missing values to impute.
        correlation_threshold (float): Minimum absolute correlation to consider a feature.
        min_strong_features (int): Minimum number of strongly correlated features required for KNN.
        n_neighbors (int): Number of neighbors to use for KNN imputation.

    Returns:
        pd.DataFrame: The DataFrame with the target column imputed.
    """
    column=get_shared_var('current_column')

    # Ensure column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    # Ensure the column is numeric
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(f"Column '{column}' must be numeric for KNN imputation.")

    # Compute correlation with other numeric features
    numeric_features = df.select_dtypes(include=[np.number]).columns.drop(column, errors='ignore')

    if len(numeric_features) > 0:
        correlation_series = df[numeric_features].corrwith(df[column], method='pearson')

        # Filter features with meaningful correlation
        strong_correlated_features = correlation_series[correlation_series.abs() >= correlation_threshold].index.tolist()
        num_strong_features = len(strong_correlated_features)
    else:
        strong_correlated_features = []
        num_strong_features = 0

    # Select only the relevant features for KNN
    knn_features = [column] + strong_correlated_features
    df_knn = df[knn_features]

    # Initialize KNN Imputer
    imputer = KNNImputer(n_neighbors=n_neighbors)

    # Fit and transform only on relevant features
    imputed_data = imputer.fit_transform(df_knn)

    # Convert back to DataFrame
    df_imputed = pd.DataFrame(imputed_data, columns=knn_features, index=df.index)

    # Determine rounding precision based on existing values
    decimal_places = determine_max_decimal_places(df[column].dropna())

    # Round imputations to match existing decimal precision
    df_imputed[column] = df_imputed[column].round(decimal_places)

    print(f"KNN imputation applied to '{column}', rounded to {decimal_places} decimal places.")

    # Replace the original column with imputed values
    df[column] = df_imputed[column]

    return df


# Imputes are scattered near the median. The dynamics increase or decrease the impute scatter range based on data distribution and the columns min and max values.
# FUTURE OPTION : Add Eval that splits flow to this dynamic_stochastic_median_impute OR a normal_distribution_impute 
# IN GENERAL: There are a lot of ways to tighten up numeric impute handling. This can be worked on a lot more.
import numpy as np
import pandas as pd

def dynamic_stochastic_median_impute(
    df,
    iqr_factor=0.5,
    clamp_to_min_max=True,
    force_round=True
):
    """
    Imputes missing values by uniformly sampling in a window around the median,
    where the half-width of that window is iqr_factor * IQR/2 (or a variant).
    
    - IQR (interquartile range) is Q3 - Q1.
    - 'iqr_factor' controls how big the band around the median is (in terms of IQR).
    - 'clamp_to_min_max' ensures we don't go outside the observed column range.
    - 'force_round' will round back to the original column's decimal places or integer format.
    
    e.g., if iqr_factor=0.5, we set the half-width ~ (0.5 * IQR)/2 = 0.25 * IQR
    => total width of the band is 0.5 * IQR.
    => random draws are in [median - 0.25*IQR, median + 0.25*IQR].
    """
    column = get_shared_var('current_column')

    # 1) Basic checks
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(f"Column '{column}' must be numeric for imputation.")
    
    # 2) Basic stats
    median_val = df[column].median()
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1  # could be 0 if all data are identical or very narrow range
    min_val = df[column].min()
    max_val = df[column].max()

    # Check for no missing values
    null_mask = df[column].isnull()
    num_nulls = null_mask.sum()
    if num_nulls == 0:
        return df  # Nothing to do

    # 3) If IQR is effectively zero, fallback to simple median fill or minimal random offset
    if iqr < 1e-9:
        # The data has almost no variation
        # fallback: fill with median (or add a tiny random offset)
        df.loc[null_mask, column] = median_val  # deterministic fill
        return df

    # 4) Define the random band around the median
    half_width = (iqr_factor * iqr) / 2.0
    low = median_val - half_width
    high = median_val + half_width

    # 5) (Optional) clamp to real observed min/max so we don't exceed the dataset range
    if clamp_to_min_max:
        low = max(low, min_val)
        high = min(high, max_val)

    # 6) Draw uniform random values in [low, high]
    imputed_values = np.random.uniform(low, high, size=num_nulls)

    # 7) (Optional) rounding
    if force_round:
        decimal_places = determine_max_decimal_places(df[column].dropna())
        imputed_values = np.round(imputed_values, decimals=decimal_places)

    # **Fix: Ensure integer columns remain integers**
    if pd.api.types.is_integer_dtype(df[column]):
        imputed_values = imputed_values.astype(int)

    # 8) Place the imputed values into the DataFrame
    df.loc[null_mask, column] = imputed_values

    print(
        f"Dynamic stochastic median imputation on '{column}' with median={median_val:.2f}, "
        f"IQR={iqr:.2f}, factor={iqr_factor}, window=[{low:.2f}, {high:.2f}] "
        f"({num_nulls} values imputed){' (rounded)' if force_round else ''}."
    )
    return df



# Used to round imputed numbers appropriate to column data
def determine_max_decimal_places(series):
    """
    Determines the maximum number of decimal places present in a numeric column.

    Args:
        series (pd.Series): The numeric column.

    Returns:
        int: Maximum decimal places detected.
    """
    # Ignore NaNs
    series = series.dropna()

    # If all values are integers, return 0 (round to whole numbers)
    if all(series.astype(int) == series):
        return 0

    # Compute max decimal places by checking number of digits after decimal
    max_decimals = series.astype(str).apply(lambda x: len(x.split(".")[1]) if "." in x else 0).max()

    return max_decimals
# endregion
# ============================================================================================#
#    region            NULL HANDLING CHAIN (Numeric as Categorical)                           #
#=============================================================================================#


# In Categorical Nums - Decide if Nulls should be their own category by checking correlation to target.
# Notes: If the target is freeform text with thousands of unique labels, your crosstab can blow up. You might need a pre-check (e.g., skip chi-square if cardinality > 50 or so, or do a more scalable approach).

from scipy.stats import chi2_contingency, fisher_exact

# This is used for both numeric and object/text columns
def evaluate_null_correlation_with_target(
    df,
    numeric_correlation_threshold=0.5,
    chi2_pvalue_threshold=0.05,
    max_categories=50
):
    """
    Evaluates whether the null pattern in a column has a strong association 
    with the target, handling numeric, boolean, and categorical/text targets.

    Fixes:
    - Prevents zero-variance issues from returning NaN.
    - Ensures meaningful results are always provided.
    - Adds debug printouts for investigating unexpected NaN outputs.

    Returns:
        dict with:
            - null_target_association: correlation or chi-square p-value.
            - high_null_association: bool, indicates strong association.
            - recommended_handling: "convert_to_category" or "impute".
    """
    column = get_shared_var('current_column')
    target = get_shared_var('target_column')

    if column not in df.columns or target not in df.columns:
        raise ValueError("One or more specified columns do not exist in the DataFrame.")

    # If no missing values, return early
    if df[column].isnull().sum() == 0:
        return {
            "null_target_association": float('nan'),
            "high_null_association": False,
            "recommended_handling": "impute",
        }
    
    null_indicator = df[column].isnull().astype(int)
    target_dtype = df[target].dtype

    # Step 1: Determine Target Type First
    unique_target_values = df[target].dropna().unique()
    num_unique_target_values = len(unique_target_values)

    if pd.api.types.is_numeric_dtype(target_dtype):
        if num_unique_target_values == 2:
            target_type = "binary_numeric"  # Binary 0/1 target
        else:
            target_type = "continuous_numeric"  # Continuous numeric target
    else:
        target_type = "categorical"

    print(f"Determined Target Type: {target_type}")

    #Step 2: Check for Zero Variance (Prevents NaN Issues)
    if null_indicator.nunique() == 1:
        print("Warning: Null indicator has no variance (all values are the same).")
        return {
            "null_target_association": float('nan'),
            "high_null_association": False,
            "recommended_handling": "impute"
        }

    if df[target].nunique() == 1:
        print("Warning: Target column has no variance (only one unique value).")
        return {
            "null_target_association": float('nan'),
            "high_null_association": False,
            "recommended_handling": "impute"
        }

    #Step 3: Apply the Correct Test Based on Target Type
    
    #### **Case 1: Continuous Numeric Target → Pearson Correlation**
    if target_type == "continuous_numeric":
        corr_value = null_indicator.corr(df[target])
        if pd.isna(corr_value):
            print("Warning: Pearson correlation is NaN due to zero variance or missing data.")
            return {
                "null_target_association": float('nan'),
                "high_null_association": False,
                "recommended_handling": "impute"
            }
        high_null_association = abs(corr_value) >= numeric_correlation_threshold
        return {
            "null_target_association": corr_value,
            "high_null_association": high_null_association,
            "recommended_handling": "convert_to_category" if high_null_association else "impute"
        }

    #### **Case 2: Binary Numeric Target → Phi Coefficient**
    elif target_type == "binary_numeric":
        # Option 1: Lower the correlation threshold
        corr_value = np.corrcoef(null_indicator, df[target])[0, 1]
        high_null_association = abs(corr_value) >= numeric_correlation_threshold

        # Option 2: Use contingency table and Fisher's Exact Test
        contingency = pd.crosstab(null_indicator, df[target])
        if contingency.shape == (2, 2):
            _, p_val = fisher_exact(contingency)
            # Consider association high if p-value is very low
            high_null_association = p_val < chi2_pvalue_threshold or high_null_association

        # Option 3: Compare conditional probabilities
        prob_when_null = df[target][df[column].isnull()].mean()
        prob_when_not_null = df[target][~df[column].isnull()].mean()
        # For instance, if the gap is larger than 0.4, flag it:
        if (prob_when_null - prob_when_not_null) > 0.4:
            high_null_association = True

        return {
            "null_target_association": corr_value,
            "high_null_association": high_null_association,
            "recommended_handling": "convert_to_category" if high_null_association else "impute"
        }

    #### **Case 3: Categorical Target → Chi-Square or Fisher’s Exact Test**
    else:
        target_str = df[target].astype(str)

        # Auto-bin high-cardinality categorical targets
        unique_count = target_str.nunique()
        if unique_count > max_categories:
            print(f"Warning: Target '{target}' has high cardinality ({unique_count} unique values). Reducing categories to {max_categories}.")
            top_categories = target_str.value_counts().nlargest(max_categories).index
            target_str = target_str.apply(lambda x: x if x in top_categories else "Other")

        # Create contingency table
        contingency_df = pd.crosstab(null_indicator, target_str, dropna=False)

        # Debugging: Print contingency table
        print("Contingency Table for Null Indicator vs Target:")
        print(contingency_df)

        # If only one row or column, switch to Fisher’s Exact Test
        if contingency_df.shape[0] < 2 or contingency_df.shape[1] < 2:
            print("Warning: Contingency table is too small for Chi-square or Fisher’s test.")
            return {
                "null_target_association": float('nan'),
                "high_null_association": False,
                "recommended_handling": "impute"
            }

        # Use Fisher’s Exact Test for 2x2 tables, Chi-square otherwise
        if contingency_df.shape == (2, 2):
            _, p_val = fisher_exact(contingency_df)
        else:
            chi2, p_val, _, _ = chi2_contingency(contingency_df)

        high_null_association = (p_val < chi2_pvalue_threshold)
        return {
            "null_target_association": p_val,
            "high_null_association": high_null_association,
            "recommended_handling": "convert_to_category" if high_null_association else "impute"
        }

# Basic Mode Imputation
def impute_categorical_numeric_mode(df):
    """
    Imputes missing values in a numeric-categorical column using mode.

    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column (str): The categorical numeric column to process.

    Returns:
        pd.DataFrame: The updated DataFrame with missing values imputed.
    """
    column=get_shared_var('current_column')
    
    # Ensure column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    # Compute mode (most frequent value)
    mode_value = df[column].mode()[0]

    # Fill missing values with mode
    df[column].fillna(mode_value, inplace=True)

    print(f"Column '{column}': Missing values imputed using mode ({mode_value}).")
    return df


# endregion
# ============================================================================================#
#    region            OBJECT and or NUMERIC COLUMN HANDLING                                                 #
#=============================================================================================#

import unicodedata

def basic_text_preprocess(df):
    """
    Cleans and standardizes a categorical text column:
    - Converts to lowercase (only for non-null values)
    - Strips leading/trailing spaces
    - Normalizes unicode characters (e.g., café → cafe)
    - Preserves special characters like "-" and "/"
    - Ensures NaNs remain unchanged

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the column.

    Returns:
    - pd.DataFrame: Updated DataFrame with cleaned categorical column.
    """
    column = get_shared_var('current_column')

    if column not in df.columns:
        return df  # Return unchanged if column is missing

    # Process only non-null values to avoid replacing NaN with "nan"
    df[column] = df[column].apply(
        lambda x: (
            unicodedata.normalize('NFKD', str(x).strip().lower()) if pd.notna(x) else x
        )
    )

    return df


def determine_if_is_categorical(df, categorical_threshold=0.2, dominant_threshold=0.9):
    """
    Determines whether an object (text) column should be handled as categorical.
    
    Classification is based on:
    - Unique-to-total ratio (low ratio suggests categorical).
    - Dominant value ratio (one category dominating suggests categorical).
    - Average character count per entry (longer text suggests NLP-style text).

    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        categorical_threshold (float): If unique-to-total ratio is below this, it's categorical.
        dominant_threshold (float): If one category dominates beyond this threshold, it's categorical.

    Returns:
        dict: A dictionary containing the column type, decision reasoning, and average character count.
    """

    column = get_shared_var('current_column')

    # Ensure the column exists
    if column not in df.columns:
        return {"error": f"Column '{column}' does not exist in the DataFrame."}

    # Ensure column is object (text)
    if not pd.api.types.is_object_dtype(df[column]):
        return {"error": f"Column '{column}' is not an object (text) data type."}

    # Remove NaN values before analysis
    column_data = df[column].dropna()

    # Count unique values and their frequencies
    unique_values = column_data.value_counts(normalize=True)  # Frequencies as proportions

    # Analyze the unique-to-total ratio
    unique_count = column_data.nunique()
    total_count = len(column_data)
    unique_ratio = unique_count / total_count if total_count > 0 else 0

    # Identify the most dominant value ratio
    dominant_value_ratio = unique_values.iloc[0] if len(unique_values) > 0 else 0

    # Compute the average character count per entry
    avg_char_count = column_data.str.len().mean() if total_count > 0 else 0

    # Decision logic: When should text be considered categorical?
    if unique_ratio < categorical_threshold or dominant_value_ratio > dominant_threshold:
        column_type = "categorical"
    elif avg_char_count <= 40:
        column_type = "short_text"  # Typically short labels, codes, names, etc.
    else:
        column_type = "long_text"  # Likely NLP-style text (paragraphs, descriptions, etc.)


    return {
        #"column": column,
        "column_type": column_type,
        #"unique_ratio": unique_ratio,
        #"dominant_value_ratio": dominant_value_ratio,
    }


def object_mode_impute(df):
    """
    Imputes missing values in an object (string/categorical) column using mode.
    If there are multiple modes, uses the first one.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        The column name is retrieved from get_shared_var('current_column').
    
    Returns:
        pd.DataFrame: The updated DataFrame with missing values imputed.
    """
    column = get_shared_var('current_column')
    
    # Ensure column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    # Ensure column is of object type
    if not pd.api.types.is_object_dtype(df[column]):
        raise ValueError(f"Column '{column}' must be of object dtype for object mode imputation.")

    # Count nulls before imputation
    null_count = df[column].isnull().sum()
    if null_count == 0:
        print(f"No missing values found in column '{column}'. No imputation needed.")
        return df

    # Compute mode (most frequent value)
    mode_value = df[column].mode()[0]  # Takes first mode if multiple exist

    # Assign back to df[column] to update the DataFrame
    df[column] = df[column].fillna(mode_value)

    print(f"Column '{column}': {null_count} missing values imputed using mode value '{mode_value}'.")
    return df  # Return the full updated DataFrame


def convert_nulls_to_category_new(df):
    """
    Converts null values in a numeric column to a new encoded value. For numeric columns,
    the nulls are replaced with a value that is one greater than the current maximum.
    The function also updates a global column_mappings dictionary to record this encoding.

    For non-numeric columns, it falls back to replacing nulls with the string "null_category".

    Args:
        df (pd.DataFrame): The DataFrame containing the column.
    
    Returns:
        pd.DataFrame: The updated DataFrame with nulls replaced.
    """
    column = get_shared_var('current_column')
    column_mappings = get_shared_var('column_mappings')
    
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    
    # Check if the column is numeric
    if pd.api.types.is_numeric_dtype(df[column]):
        # If there are any non-null values, set new_value to max+1; otherwise choose a default (e.g., 1)
        if df[column].notnull().any():
            max_value = df[column].max()
            new_value = max_value + 1
        else:
            new_value = 1

        num_nulls = df[column].isnull().sum()
        df.fillna({column: new_value}, inplace=True)
        # df[column].fillna(new_value, inplace=True) #Depricated

        print(f"Converted {num_nulls} nulls in '{column}' to encoded value {new_value}.")

        # Update column_mappings for this column
        if column in column_mappings:
            column_mappings[column]['null_encoding'] = new_value
        else:
            column_mappings[column] = {'null_encoding': new_value}
    
    else:
        # For non-numeric columns, revert to a string replacement.
        num_nulls = df[column].isnull().sum()
        df.fillna({column: "null_category"}, inplace=True)
        # df[column].fillna("null_category", inplace=True) #Depricated
        print(f"Converted {num_nulls} nulls in '{column}' to category 'null_category'.")

    return df

def display_unique_entry_batches(df, batch_size=20,
                                 batch_first=False, batch_second=False,
                                 batch_second_to_last=False, batch_last=False):
    """
    Displays batches of unique entries in a column based on their frequency.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column (str): The column to analyze.
        batch_size (int, optional): The size of each batch. Default is 20.
        batch_first (bool, optional): Whether to display the first batch (most common entries). Default is False.
        batch_second (bool, optional): Whether to display the second batch (next most common entries). Default is False.
        batch_second_to_last (bool, optional): Whether to display the second to last batch (least common entries before the last batch). Default is False.
        batch_last (bool, optional): Whether to display the last batch (least common entries). Default is False.
        
    Returns:
        pd.DataFrame: A DataFrame containing the selected batches.
    """
    column = get_shared_var('current_column')
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

# Get unique entries in the order they appear
    unique_entries = df[column].dropna().unique()  # Excludes NaN values

    # Define the batches
    batches = {}

    if batch_first:
        batches["Batch 1"] = unique_entries[:batch_size]

    if batch_second:
        batches["Batch 2"] = unique_entries[batch_size:2*batch_size]

    if batch_second_to_last:
        batches["Batch 3"] = unique_entries[-2*batch_size:-batch_size]

    if batch_last:
        batches["Batch 4"] = unique_entries[-batch_size:]

    return batches

    # Option 2: Display using IPython's display if available, otherwise print it.
    # try:
    #     from IPython.display import display
    #     display(batch_df)
    # except ImportError:
    #     print(batch_df)


def count_unique_entries(df):
    """
    Counts the total number of unique entries in a specified DataFrame column.

    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column (str): The column name to count unique entries.

    Returns:
        int: The number of unique entries in the column.
    """
    column = get_shared_var('current_column')
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    
    unique_count = df[column].nunique()
    print(f"Column '{column}' has {unique_count} unique entries.")
    
    return unique_count


# Temp Display Dictionary Function
def display_redundancy_dictionary():
    """
    Retrieves and returns the current redundancy dictionary from shared variables.
    
    Returns:
        dict: The current redundancy dictionary (or an empty dict if not set).
    """
    redundancy_dict = get_shared_var('redundancy_dictionary')
    if redundancy_dict is None:
        redundancy_dict = {}
    return redundancy_dict

# endregion