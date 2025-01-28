#==============================================================================#
#        This is a place to quickly test functions outside of LLM calls        #
#==============================================================================#   
import pandas as pd
from runtime_lib.static_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)


# Iterate over Each Column in the DF
for column in df:
    # Skip Target Variable
    if column == "target":
        # Skip processing for the 'target' column
        continue

    # COLUMN(S) TO TEST ON
    COLUMNS_TO_TEST = ["col3"]
    if column not in COLUMNS_TO_TEST:
        # Skip processing for all columns except 'COLUMNS_TO_TEST'.
        continue
            
    #current_column = column
    
    #=======================================================#
    #        TEST FUNCTION GOES HERE                        #
    #=======================================================#   


    print(
        # insert function to test
        #data_type_check(df, column)
        #data_type_check(df,column="col3"),
        #check_percent_numeric(df, column="col3", numeric_threshold=0.9),
        #convert_text_nums_to_numeric(df, column="col3"),
        #describe_and_clean_non_numeric_entries(df, column="col3"),
        cap_outliers_and_impute_nulls(df, column="col2")
        )