def handle_null_values(df):
    """
    This function handles null values in the DataFrame by filling them with the mean of their respective columns.
    Args:
        df (pandas.DataFrame): The input DataFrame with potential null values.
    Returns:
        pandas.DataFrame: The DataFrame with null values handled.
    """
    # Fill null values with the mean of their respective columns
    return df.fillna(df.mean())

