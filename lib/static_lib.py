# No unreviewed generated code is contained in this file

# Every function should ideally have a [description]: field within its docstring

import pandas as pd

def drop_df_duplicates(df):
    '''
    [description]: Drops duplicate rows from a DataFrame "in place"
    '''
    start_rows = len(df)
    df.drop_duplicates(inplace=True)
    end_rows = len(df)

    return f'Dropped {start_rows - end_rows} duplicate rows. There are {end_rows} remaining rows.'