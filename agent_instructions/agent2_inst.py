AGENT2_IA = {
#=============================================================================================#
#    region                AGENT2   OUTLIERS AND NULL IMPUTING                                #
#=============================================================================================#
    "AGENT2_START": (
        "Use the exec_stored_func tool to run the data_type_check function to determine the Column's data type.\n"
        "State the column's data type.\n"
        "If data type is Float, use the tool call get_inst(FLOAT_INST) for instructions.\n"
        "If data type is Integer, use the tool call get_inst(NUMERIC_INST) for instructions.\n"
        "If data type is Object, use the tool call get_inst(OBJECT_INST) for instructions.\n"
        "If data type is any other type, use the tool call get_inst(UNKNOWN_INST) for instructions.\n"
    ),

    # Instructions for handling Float data type columns.
    "FLOAT_INST": (
        "Use exec_stored_func tool to run if_float_is_really_int_convert.\n"
        "Follow instructions from the call get_inst(NUMERIC_INST).\n"
    ), # Instructions for handling Integer data type columns.
    "NUMERIC_INST": (
        "Use exec_stored_func tool to run determine_numeric_or_categorical to determine if the column is truly numeric or if it is categroical.\n"
        "If returned column_type = numeric, use the tool call get_inst(NUMERIC_NULL_AND_OUTLIER_INST) for instructions.\n"
        "If returned column_type = categorical, use the tool call get_inst(CATEGORICAL_NULL_AND_OUTLIER_INST) for instructions.\n"
    ), # Instructions for handling numeric columns.
    "NUMERIC_NULL_AND_OUTLIER_INST": (
        # Scattered winsorizing?
        # Use new KNN and Stochastic Median chain when ready.
        "Use exec_stored_func tool to run check_outliers_and_nulls to find and describe outliers and or nulls \n"
        "If Warnings are Present use the logger tool to write the document the warning in the pipeline.\n"
        "If outliers AND OR nulls are present, use exec_stored_func tool to run cap_outliers_and_impute_nulls.\n"
    ), # Instructions for handling Categorical numeric columns.
    "CATEGORICAL_NULL_AND_OUTLIER_INST": (
        "Say that this numeric column is categorical in nature. \n"
        #"Use exec_stored_func tool to run SOMETHING ABOUT CATEGORIES to work with \n"
        #"If nulls are present, Use exec_stored_func tool to run impute_mode_or_create_exnulls_cat \n"
    ),
    
}