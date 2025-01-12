import pandas as pd

def remove_duplicates(df):
    initial_len = len(df)
    df.drop_duplicates(inplace=True)
    final_len = len(df)
    removed_rows = initial_len - final_len
    return f'Removed {removed_rows} duplicate rows. The data frame now has {final_len} rows.'