def check_nulls(df):\n    """Check for null values in the DataFrame and return a boolean value and a count of nulls."""\n    null_count = df.isnull().sum().sum()  # Count total null values\n    has_nulls = null_count > 0  # Check if there are any nulls\n    return has_nulls, null_count  # Return a tuple of (has_nulls, null_count)

