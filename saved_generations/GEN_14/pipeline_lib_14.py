
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Iterate through each column in the row
        for col in df.columns:
            if isinstance(row[col], str):  # Check if the cell contains a string
                # Fix spelling errors using TextBlob
                corrected_text = str(TextBlob(row[col]).correct())
                df.at[index, col] = corrected_text  # Update the DataFrame with corrected text
    return df


def analyze_fixed_spelling(df):
    # Check if there are any remaining spelling errors by comparing original and corrected text
    errors_found = False
    for index, row in df.iterrows():
        for col in df.columns:
            if isinstance(row[col], str):
                # Use TextBlob to check for spelling errors
                if str(TextBlob(row[col]).correct()) != row[col]:
                    errors_found = True
                    print(f"Spelling error found in row {index}, column '{col}': {row[col]}")
    return not errors_found  # Return True if no errors found, False otherwise


def remove_duplicates(df):
    # Remove duplicate rows from the DataFrame
    return df.drop_duplicates()


def analyze_data(df):
    # Analyze the DataFrame to confirm duplicates have been removed
    return df.shape[0], df.duplicated().sum()


def handle_null_values(df):
    """
    Function to handle null values in the DataFrame.
    This function will fill null values with the mean of the respective column for numerical columns,
    and with the mode for categorical columns.
    """
    # Identify numerical and categorical columns
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # Fill null values in numerical columns with the mean
    for col in numerical_cols:
        df[col].fillna(df[col].mean(), inplace=True)

    # Fill null values in categorical columns with the mode
    for col in categorical_cols:
        df[col].fillna(df[col].mode()[0], inplace=True)

    return df


def analyze_null_handling(df):
    """
    Function to analyze the DataFrame after handling null values.
    This function will return the count of null values in each column to confirm that all nulls have been handled.
    """
    null_counts = df.isnull().sum()  # Count null values in each column
    return null_counts


