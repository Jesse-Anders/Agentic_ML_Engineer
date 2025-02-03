AGENT2_IA = {
#=============================================================================================#
#    region                AGENT2   OUTLIERS AND NULL IMPUTING                                #
#=============================================================================================#
    "AGENT2_START": (
        # FUTURE WORK:Look over for BOOL and CATEGORICAL TYPE handling
        "Use the exec_stored_func tool to run the data_type_check function to determine the Column's data type.\n"
        "If data type is Float, use the tool call get_inst(FLOAT_INST) for instructions.\n"
        "If data type is Integer, use the tool call get_inst(NUMERIC_INST) for instructions.\n"
        "If data type is Object, use the tool call get_inst(OBJECT_INST) for instructions.\n"
        "If data type is any other type, use the tool call get_inst(UNKNOWN_INST) for instructions.\n"
    ),

    # Instructions for handling Float data type columns.
    "FLOAT_INST": (
        "Use exec_stored_func tool to run if_float_is_really_int_convert.\n"
        "Follow instructions from the call get_inst(NUMERIC_INST).\n"
    ), 
    # Instructions for handling Integer data type columns.
    "NUMERIC_INST": (
        "Use exec_stored_func tool to run determine_numeric_or_categorical to determine if the column is truly numeric or if it is categroical.\n"
        "If returned column_type = numeric, use the tool call get_inst(NUMERIC_OUTLIER_INST) for instructions.\n"
        "If returned column_type = categorical, use the tool call get_inst(CATEGORICAL_NULL_INST) for instructions.\n"
    ), 
    # Instructions for handling numeric outliers.
    "NUMERIC_OUTLIER_INST": (
        "Use exec_stored_func tool to run evaluate_outliers to get outlier handling recommendations.\n"
        "If 'keep' is recommended, use tool call get_inst(NUMERIC_NULL_INST) for instructions.\n"
        "If 'winsorize' is recommended, use exec_stored_func to run winsorize_column. Then use tool call get_inst(NUMERIC_NULL_INST) for instructions.\n"
        "If 'transform' is recommended, use exec_stored_func to run log_transform_column. Then use tool call get_inst(NUMERIC_NULL_INST) for instructions.\n"
        # Consider updateing evaluate_outliers to include a 'further investigation needed' recommendation.
    ),
    # Instructions for imputing numeric nulls.
    "NUMERIC_NULL_INST": (
        "Use exec_stored_func tool to run evaluate_imputation_strategy to get null handling recommendations.\n"
        "If 'stochastic median' is recommended, use exec_stored_func tool to run dynamic_stochastic_median_impute. END PROCESS.\n"
        "If 'KNN' is recommended, use exec_stored_func tool to run knn_impute_with_rounding. END PROCESS.\n"
    ),
    # Instructions for handling numeric as categorical nulls.
    "CATEGORICAL_NULL_INST": (
        "Use exec_stored_func tool to run evaluate_null_correlation_with_target to get null handling recommendations.\n"
        "If 'convert_to_category' is recommended, use exec_stored_func tool to run convert_nulls_to_category. Then use tool call get_inst(CATEGORICAL_ENCODE_EXNULLS_CATEGORY) for instructions.\n"
        "If 'impute' is recommended, use exec_stored_func tool to run impute_categorical_numeric_mode. END PROCESS.\n"
    ),
    # Instructions for encoding new Null as Category Column.
    "CATEGORICAL_ENCODE_EXNULLS_CATEGORY": (
        # STILL UNDER CONSTRUCTION!! Need to encode exNull to revert now object column back to integer or float.
        "Column still needs to be converted back to numeric after exNull category created. END PROCESS.\n"\
    ),
# endregion
# ============================================================================================#
#    region                            DEAD ENDS TO WORK ON                                   #
#=============================================================================================#
    # Instructions for handling Object data type columns.
    "OBJECT_INST": (
        "Tell me you have read the Object instructions. And say Thank You. \n"
    ),
    # Instructions for handling Unknown data type columns.
    "UNKNOWN_INST": (
        "Tell me you have read the Unknown instructions. And say Thank You. \n"
    )
    # endregion
}