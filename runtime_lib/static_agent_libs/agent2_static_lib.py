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
from scipy.stats import chi2_contingency
def evaluate_null_correlation_with_target(
    df,
    numeric_correlation_threshold=0.5,
    chi2_pvalue_threshold=0.05
):
    """
    Evaluates whether the null pattern in `column` has a strong association 
    with the `target`, which can be numeric, boolean, or categorical/text.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The name of the column for which we're evaluating nulls.
        target (str): The name of the target column.
        numeric_correlation_threshold (float): For numeric/boolean targets, the 
            absolute Pearson correlation needed to consider null as a separate category.
        chi2_pvalue_threshold (float): For categorical/text targets, the p-value 
            cutoff from a chi-square test of independence. If below this threshold, 
            we consider the association “strong enough” to treat null separately.
    
    Returns:
        dict with:
            - null_target_association: numeric correlation or chi-square p-value 
              (depending on target type).
            - high_null_association: bool, indicates "strong enough" association.
            - recommended_handling: "convert_to_category" or "impute".
    """
    column=get_shared_var('current_column')
    target=get_shared_var('target_column')

    # 1. Basic validation checks
    if column not in df.columns or target not in df.columns:
        raise ValueError("One or more specified columns do not exist in the DataFrame.")

    # If no missing data at all, no reason to do anything special
    if df[column].isnull().sum() == 0:
        return {
            "null_target_association": 0.0,
            "high_null_association": False,
            "recommended_handling": "impute",  # or "none" if you prefer
        }
    
    # Create a binary indicator for missing values in `column`
    null_indicator = df[column].isnull().astype(int)

    # 2. Handle different target types
    target_dtype = df[target].dtype
    # We'll unify the logic into two broad branches:
    #   - "Numeric/Boolean" => Pearson correlation
    #   - "Categorical/Text/Other" => Chi-square test

    # Check for boolean:
    #   Pandas sometimes stores booleans as bool dtype or object dtype with True/False
    #   We'll cast if it's purely True/False. Then we can do correlation as 0/1 if we want.
    # Or decide it's effectively "categorical" if it's string-based or object-based.
    
    if pd.api.types.is_numeric_dtype(target_dtype):
        # Could be float, int, or possibly a boolean column stored as bool
        # If bool, let's cast it to numeric so we can do correlation
        if df[target].dropna().isin([0,1]).all():
            # It's effectively numeric binary => correlation is fine
            # (Pearson correlation with a 0/1 target is the same as a phi coefficient)
            pass
        else:
            # It's a real numeric variable or possibly more than just 0/1
            pass
        
        # 2a. Pearson correlation approach
        corr_value = null_indicator.corr(df[target])
        
        # Check for NaN or no variance issues
        if pd.isna(corr_value):
            # e.g. if target or null_indicator had zero variance => correlation is undefined
            return {
                "null_target_association": float('nan'),
                "high_null_association": False,  
                "recommended_handling": "impute"
            }

        # Evaluate if it's beyond threshold
        high_null_association = abs(corr_value) >= numeric_correlation_threshold

        # Decide recommended handling
        recommended_handling = "convert_to_category" if high_null_association else "impute"

        return {
            "null_target_association": corr_value,
            "high_null_association": high_null_association,
            "recommended_handling": recommended_handling
        }

    else:
        # 2b. Categorical or text target => let's do a chi-square test
        # Build a contingency table of:
        #  rows = null_indicator(0/1), columns = categories in the target
        # If the target has extremely high cardinality (like freeform text), 
        # this might get large. But let's attempt it.

        # Convert target to string (just in case) to group by unique categories
        target_str = df[target].astype(str)

        contingency_df = pd.crosstab(null_indicator, target_str, dropna=False)

        # If there's only 1 row or 1 column in the contingency, chi2 is not well-defined
        if contingency_df.shape[0] < 2 or contingency_df.shape[1] < 2:
            # Means either all null or no null, or the target has only 1 unique value
            return {
                "null_target_association": float('nan'),
                "high_null_association": False,
                "recommended_handling": "impute"
            }

        chi2, p_val, dof, ex = chi2_contingency(contingency_df)

        # If p_val < threshold => means "strong association" between null-indicator & target category
        high_null_association = (p_val < chi2_pvalue_threshold)

        recommended_handling = "convert_to_category" if high_null_association else "impute"

        return {
            "null_target_association": p_val,  # storing the p-value as the association measure
            "high_null_association": high_null_association,
            "recommended_handling": recommended_handling
        }



# Convert Nulls to exNulls if they are highly correlated to the target feature
# WARNING: This turns the column into object type to accomodate non-encoded "null_category" entries.
def convert_nulls_to_category(df, category_label="null_category"):
    """
    Converts null values in a column to a categorical label.

    Args:
        df (pd.DataFrame): The DataFrame containing the column.
        column (str): The column to process.
        category_label (str): The label to replace null values with (default: "Missing").

    Returns:
        pd.DataFrame: The updated DataFrame with nulls converted to a category.
    """
    column=get_shared_var('current_column')

    # Ensure the column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")

    # Count number of nulls before replacement
    num_nulls = df[column].isnull().sum()

    # Replace nulls with the specified category label
    df[column].fillna(category_label, inplace=True)

    print(f"Converted {num_nulls} nulls in '{column}' to category '{category_label}'.")
    
    return df


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