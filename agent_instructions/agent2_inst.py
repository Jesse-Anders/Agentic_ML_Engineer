# TO DO: IMPORTANT: The redundancy_dictionary needs to be updated to run off a json so there is a permanent record of the changes

object_4_general_instructions = """
Look closely at the Function Output and determine if any of the unique entries seem like duplicate entries but have slight differences.
There may be differences such as spelling errors, or duplicate entries may have added extraneous characters such as brackets, dashes or parentheses.
Be thorough and complete, making comprehensive comparisons between all the items when searching for potential duplicates.
For all entries that you are EXTREMELY confident are duplicates, use the redundancy_dictionary tool to add items as Keys & Values to the redundancy_dict.
"""

AGENT2_IA = {
#=============================================================================================#
#    region                AGENT2   OUTLIERS AND NULL IMPUTING                                #
#=============================================================================================#
# Temp jump to object batcher
    "AGENT2_START": (
        #"Use tool call get_inst(OBJECT_INST_3) for further instructions."
        "Use exec_stored_func too to run drop_column()"
        "Else, END PROCESS."
    ),

    # "AGENT2_START": (
    #     "Use the exec_stored_func tool to run the data_type_check(df) function to determine the Column's data type.\n"
    #     "If data type is Float, use the tool call get_inst(FLOAT_INST) for instructions.\n"
    #     "If data type is Integer, use the tool call get_inst(NUMERIC_INST) for instructions.\n"
    #     "If data type is Object, use the tool call get_inst(BOOL_CHECK_INST) for instructions.\n"
    #     "If data type is Boolean, use the tool call get_inst(BOOL_INST) for instructions.\n"
    #     "If data type is any other type, use the tool call get_inst(UNKNOWN_INST) for instructions."
    # ),

    "BOOL_CHECK_INST": (
        "Use exec_stored_func tool to run check_for_bool(df).\n"
        "If column is determined to be boolean get_inst(BOOL_INST).\n"
        "Else, use the tool call get_inst(OBJECT_INST) for instructions."
    ),
    "BOOL_INST": (
        "Use exec_stored_func tool to run encode_bool_to_num_cat(df).\n"
        "After running encode_bool_to_num_cat(df), use the tool call get_inst(NUMERIC_INST) for instructions."
    ),

    # Instructions for handling Float data type columns.
    "FLOAT_INST": (
        "Use exec_stored_func tool to run if_float_is_really_int_convert(df).\n"
        "After running if_float_is_really_int_convert(df), follow instructions from the call get_inst(NUMERIC_INST)."
    ), 
    # Instructions for handling Integer data type columns.
    "NUMERIC_INST": (
        "Use exec_stored_func tool to run determine_numeric_or_categorical(df) to determine if the column is truly numeric or if it is categroical.\n"
        "If returned column_type = numeric, use the tool call get_inst(NUMERIC_OUTLIER_INST) for instructions.\n"
        "If returned column_type = categorical, use the tool call get_inst(CATEGORICAL_NULL_INST) for instructions.\n"
    ), 
    # Instructions for handling numeric outliers.
    "NUMERIC_OUTLIER_INST": (
        # Potential Update to Handle low numbers of 'extreme' outliers.
        "Use exec_stored_func tool to run evaluate_outliers(df) to get outlier handling recommendations.\n"
        "If 'keep' is recommended, use tool call get_inst(NUMERIC_NULL_INST) for instructions.\n"
        "If 'winsorize' is recommended, use exec_stored_func to run winsorize_column(df). Then use tool call get_inst(NUMERIC_NULL_INST) for instructions.\n"
        "If 'transform' is recommended, use exec_stored_func to run log_transform_column(df). Then use tool call get_inst(NUMERIC_NULL_INST) for instructions.\n"
        # Consider updateing evaluate_outliers to include a 'further investigation needed' recommendation.
    ),
    # Instructions for imputing numeric nulls.
    "NUMERIC_NULL_INST": (
        "Use exec_stored_func tool to run evaluate_imputation_strategy(df) to get null handling recommendations.\n"
        "If 'stochastic median' is recommended, use exec_stored_func tool to run dynamic_stochastic_median_impute. END PROCESS.\n"
        "If 'KNN' is recommended, use exec_stored_func tool to run knn_impute_with_rounding. END PROCESS.\n"
    ),
    # Instructions for handling numeric as categorical nulls.
    "CATEGORICAL_NULL_INST": (
        "Use exec_stored_func tool to run evaluate_null_correlation_with_target(df) to get null handling recommendations.\n"
        # NEED NEW LOGIC HERE... The convert_nulls_to_category_new encodes new null_category as 1 number higher than the highest number in the data set.
        "If 'convert_to_category' is recommended, use exec_stored_func tool to run convert_nulls_to_category_new(df).\n"
        # THIS SHOULD BE UPGRADED to impute based on correlation or knn etc when possible, rather than always MODE impute.
        "If 'impute' is recommended, use exec_stored_func tool to run impute_categorical_numeric_mode(df). END PROCESS."
    ),

#    endregion  ==============================================================================#
#    region                            OBJECT COLUMNS                                         #
#=============================================================================================#
    # Instructions for handling Object data type columns.

    "OBJECT_INST": (
        "Use exec_stored_func tool to run basic_text_preprocess(df).\n"
        "Use exec_stored_func tool to run evaluate_null_correlation_with_target(df) to get null handling recommendations.\n"
        "If 'convert_to_category' is recommended, use exec_stored_func tool to run convert_nulls_to_category_new(df).\n"
        # Could maybe upgrade to include a correlation or knn impute in addition to basic mode impute
        "Else, use the exec_stored_func tool to run object_mode_impute(df).\n"
        "Now, use tool call get_inst(OBJECT_INST_2) for further instructions."
    ),
    "OBJECT_INST_2": (
        "Use exec_stored_func tool to run determine_if_is_categorical(df)\n"
        "If Function Return column_type as 'categorical', use tool call get_inst(OBJECT_INST_2-1) for further instructions.\n"
        "If Function Return column_type as 'short_text', use tool call get_inst(OBJECT_INST_3) for further instructions.\n" # Send to cleaning of top 40 unique entries
        "If Function Return column_type as 'long_text', END PROCESS."    
    ),
    "OBJECT_INST_2-1": (
        # NEED A RUN_REDUNDANCY=True/False parameter to open this up or close it.
        "Use exec_stored_func tool to run count_unique_entries(df).\n"
        "If column has 40 or fewer unique entries, use tool call get_inst(OBJECT_INST_3) for further instructions.\n"
        "Else, if column has 41 or more unique entries, use tool call get_inst(OBJECT_INST_4-1) for further instructions."  
    ),
    "OBJECT_INST_3": (
        # NOTE: display_most_common_unique_entries is in agent1_static_lib.py
        "Use exec_stored_func tool to run display_most_common_unique_entries(df, max_display=40).\n"
        f"{object_4_general_instructions}\n"
        "Use exec_stored_func tool to run display_redundancy_dictionary().\n"
        "Use tool call get_inst(OBJECT_3_AND_4_HUMAN_APPROVAL) for further instructions."
    ),
    "OBJECT_INST_4-1": (
        "Use exec_stored_func tool to run display_unique_entry_batches(df, batch_size=20, batch_first=True, batch_second=True)\n"
        f"{object_4_general_instructions}\n"   
        "Use tool call get_inst(OBJECT_INST_4-2) for further instructions."
    ),
    "OBJECT_INST_4-2": (
        "Use exec_stored_func tool to run display_unique_entry_batches(df, batch_size=20, batch_first=True, batch_second_to_last=True)\n"
        f"{object_4_general_instructions}\n"
        "Use tool call get_inst(OBJECT_INST_4-3) for further instructions."
    ),
    "OBJECT_INST_4-3": (
        "Use exec_stored_func tool to run display_unique_entry_batches(df, batch_size=20, batch_first=True, batch_last=True)\n"
        f"{object_4_general_instructions}\n"
        "Use tool call get_inst(OBJECT_INST_4-4) for further instructions."
    ),
    "OBJECT_INST_4-4": (
        "Use exec_stored_func tool to run display_unique_entry_batches(df, batch_size=20, batch_second=True, batch_second_to_last=True)\n"
        f"{object_4_general_instructions}\n" 
        "Use tool call get_inst(OBJECT_INST_4-5) for further instructions."
    ),
    "OBJECT_INST_4-5": (
        "Use exec_stored_func tool to run display_unique_entry_batches(df, batch_size=20, batch_second=True, batch_last=True)\n" 
        f"{object_4_general_instructions}\n"
        "Use tool call get_inst(OBJECT_INST_4-6) for further instructions."
    ),
    "OBJECT_INST_4-6": (
        "Use exec_stored_func tool to run display_unique_entry_batches(df, batch_size=20, batch_second_to_last=True, batch_last=True)\n"  
        f"{object_4_general_instructions}\n"
        "Use exec_stored_func tool to run display_redundancy_dictionary().\n"
        "Use tool call get_inst(OBJECT_3_AND_4_HUMAN_APPROVAL) for further instructions."
    ),
    "OBJECT_3_AND_4_HUMAN_APPROVAL": (
        #"Call tool request_human_approval('clean_redundant_entries')\n"
        #"If human grants approval, Use exec_stored_func tool to run clean_redundant_entries(df).\n"
        #"Else, END PROCESS."
        "End Process"
    ),

    # Instructions for handling Unknown data type columns.
    "UNKNOWN_INST": (
        "Tell me you have read the Unknown instructions. And say Thank You. \n"
    )
    # endregion
}
