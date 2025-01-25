
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Iterate through each column in the row
        for col in df.columns:
            # Check if the cell is a string
            if isinstance(row[col], str):
                # Fix spelling errors using TextBlob
                corrected_text = str(TextBlob(row[col]).correct())
                # Update the DataFrame with corrected text
                df.at[index, col] = corrected_text
    return df


def analyze_dataframe(df):
    # Display the first few rows of the DataFrame to verify changes
    return df.head()


def remove_duplicates(df):
    """
    Remove any duplicate rows from the DataFrame.
    
    Parameters:
    df : pandas.DataFrame
        The DataFrame from which duplicates will be removed.
    
    Returns:
    pandas.DataFrame
        A DataFrame with duplicates removed.
    """
    # Use the drop_duplicates method to remove duplicates
    return df.drop_duplicates()


def analyze_dataframe(df):
    """
    Analyze the DataFrame to confirm that duplicates have been removed.
    
    Parameters:
    df : pandas.DataFrame
        The DataFrame to analyze.
    
    Returns:
    None
    """
    # Print the number of rows before and after removing duplicates
    initial_count = len(df)
    df_no_duplicates = remove_duplicates(df)
    final_count = len(df_no_duplicates)
    print(f"Initial number of rows: {initial_count}")
    print(f"Number of rows after removing duplicates: {final_count}")
    
    # Check if any duplicates exist
    if initial_count == final_count:
        print("No duplicates were found.")
    else:
        print("Duplicates were removed.")


def handle_null_values(df):
    """
    This function handles null values in the DataFrame.
    It fills null values with the mean of the respective column for numerical columns
    and with the mode for categorical columns.
    """
    # Iterate through each column in the DataFrame
    for column in df.columns:
        if df[column].dtype == 'object':  # Categorical column
            # Fill null values with the mode of the column
            df[column].fillna(df[column].mode()[0], inplace=True)
        else:  # Numerical column
            # Fill null values with the mean of the column
            df[column].fillna(df[column].mean(), inplace=True)
    return df


def analyze_null_handling(df):
    """
    This function analyzes the DataFrame after handling null values.
    It returns the number of null values in each column before and after handling.
    """
    # Store the number of null values before handling
    null_counts_before = df.isnull().sum()
    # Handle null values
    df = handle_null_values(df)
    # Store the number of null values after handling
    null_counts_after = df.isnull().sum()
    return null_counts_before, null_counts_after


def review_data_types(df):
    """
    Review the data types of each column in the DataFrame to ensure they are appropriate for analysis.
    """
    # Get the data types of each column
    data_types = df.dtypes
    # Return the data types
    return data_types


def analyze_summary_statistics(df):
    # Calculate summary statistics for numerical columns in the DataFrame
    summary_stats = df.describe()
    return summary_stats


def display_summary_statistics(stats):
    # Display the summary statistics in a readable format
    print("Summary Statistics:")
    print(stats)



def handle_null_values(df):
    """
    This function handles null values in the DataFrame by filling them with the mean of their respective columns.
    If a column is non-numeric, it will fill nulls with the mode of that column.
    """
    for column in df.columns:
        if df[column].dtype in ['int64', 'float64']:
            # Fill nulls with the mean for numeric columns
            df[column].fillna(df[column].mean(), inplace=True)
        else:
            # Fill nulls with the mode for non-numeric columns
            df[column].fillna(df[column].mode()[0], inplace=True)
    return df


def analyze_null_handling(df):
    """
    This function analyzes the DataFrame to confirm that all null values have been handled.
    It returns the number of null values in each column after handling.
    """
    null_counts = df.isnull().sum()
    return null_counts


def review_data_types(df):
    # This function reviews the data types of each column in the dataframe.
    data_types = df.dtypes  # Get the data types of each column.
    return data_types


def analyze_summary_statistics(df):
    """
    Analyzes the summary statistics of numerical columns in the DataFrame to identify anomalies or outliers.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame containing numerical columns.
    
    Returns:
    pd.DataFrame: A DataFrame containing summary statistics and potential outliers.
    """
    # Generate summary statistics for numerical columns
    summary_stats = df.describe()
    
    # Identify outliers using the IQR method
    outliers = {}  # Dictionary to hold outliers for each column
    for column in df.select_dtypes(include=['number']).columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1  # Interquartile range
        lower_bound = Q1 - 1.5 * IQR  # Lower bound for outliers
        upper_bound = Q3 + 1.5 * IQR  # Upper bound for outliers
        outliers[column] = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column]
    
    return summary_stats, outliers




