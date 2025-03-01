AGENT2_IA = {
#=============================================================================================#
#    region                AGENT2   OUTLIERS AND NULL IMPUTING                                #
#=============================================================================================#
    "AGENT2_START": (
        # FUTURE WORK:Look over for BOOL and CATEGORICAL TYPE handling
        "Use the exec_stored_func tool to run the data_type_check(df) function to determine the Column's data type.\n"
        "If data type is Float, use the tool call get_inst(FLOAT_INST) for instructions.\n"
        "If data type is Integer, use the tool call get_inst(NUMERIC_INST) for instructions.\n"
        "If data type is Object, use the tool call get_inst(BOOL_CHECK_INST) for instructions.\n"
        "If data type is Boolean, use the tool call get_inst(BOOL_INST) for instructions.\n"
        "If data type is any other type, use the tool call get_inst(UNKNOWN_INST) for instructions."
    ),

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
        "If 'convert_to_category' is recommended, use exec_stored_func tool to run convert_nulls_to_category(df). Then use tool call get_inst(CATEGORICAL_ENCODE_EXNULLS_CATEGORY) for instructions.\n"
        # THIS SHOULD BE UPGRADED to impute based on correlation or knn etc when possible, rather than always MODE impute.
        "If 'impute' is recommended, use exec_stored_func tool to run impute_categorical_numeric_mode(df). END PROCESS.\n"
    ),
    # Instructions for encoding new Null as Category Column.
    "CATEGORICAL_ENCODE_EXNULLS_CATEGORY": (
        # STILL UNDER CONSTRUCTION!! Need to encode exNull to revert now object column back to integer or float.
        "Column still needs to be converted back to numeric after exNull category created. END PROCESS.\n"\
    ),

#    endregion  ==============================================================================#
#    region                            DEAD ENDS TO WORK ON                                   #
#=============================================================================================#
    # Instructions for handling Object data type columns.
    "OBJECT_INST": (
        # IMPORTANT: Incomplete. Must handle exNulls when target correlation 
        # IMPORTANT: Incomplete. Handle Categorical assimilation. 1-99 vs [1-99] vs 1 - 199 type issues
        "Use the exec_stored_func tool to run object_mode_impute(df).\n"
        "END PROCESS.\n"
    ),
    # Instructions for handling Unknown data type columns.
    "UNKNOWN_INST": (
        "Tell me you have read the Unknown instructions. And say Thank You. \n"
    )
    # endregion
}

# OBJECT_INST will handl exNull situations
# OBJECT_INST will handle Categorical determination AND categorical assimilation. 1-99 vs [1-99] vs 1 - 199 type issues.
# OBJECT_INST will mode impute