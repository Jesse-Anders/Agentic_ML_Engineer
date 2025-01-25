def check_duplicates(df):
    """
    This function checks for duplicate rows in the DataFrame.
    Returns a boolean indicating if duplicates are present and the count of duplicates.
    """
    duplicate_count = df.duplicated().sum()  # Count total duplicates in the DataFrame
    has_duplicates = duplicate_count > 0  # Check if there are any duplicates
    return has_duplicates, duplicate_count  # Return a tuple of the result and the count

