#lib_eda_static.py

def drop_df_duplicates(df):
    """
        "function_name": "drop_df_duplicates",
        "description": "Drops duplicate rows from a DataFrame in place and returns a summary string. "
    """
    #if not isinstance(df, pd.DataFrame):
    #    return "Error: input is not a valid pandas DataFrame."

    initial_len = len(df)
    df.drop_duplicates(inplace=True)
    final_len = len(df)
    return f"Dropped {initial_len - final_len} duplicate rows. Remaining rows: {final_len}."

def save_df_to_csv(df):
    """
        "function_name": "save_df_to_csv",
        "description": "Saves data frame named df as .csv file named date_cleaned.csv. "
    """
    try:
        df.to_csv('data_cleaned.csv', index=False)
        return 'Data frame saved to data_cleaned.csv'
    except Exception as e:
        return str(e)

