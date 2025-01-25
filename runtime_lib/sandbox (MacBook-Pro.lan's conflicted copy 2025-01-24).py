def remove_duplicates(df):
    """Remove duplicate rows from the DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame from which to remove duplicates.

    Returns:
        pandas.DataFrame: A DataFrame with duplicates removed.
    """
    # Use the drop_duplicates method to remove duplicate rows
    return df.drop_duplicates()

