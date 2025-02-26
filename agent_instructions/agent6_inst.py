AGENT6_IA = {
#=============================================================================================#
#    region                AGENT6                                                             #
#=============================================================================================#
    "AGENT6_START": (
        "Use the exec_stored_func to run gather_column_info to show a sampling of entries in the column.\n"
        "Decide if current column contains boolean data (true and false values only) or if the column is numeric (continuous or integer, not just codes for categories), or if the column is neither.\n"
        "If the column is true false boolean, add the current column name to the encode_selections dictionary as Encode_True_False_As_One_Zero. END PROCESS.\n"
        "If the column is numeric, add the current column name to the encode_selections dictionary as Scale_Or_Normalize. END PROCESS.\n"
        "If the column is neither bool nor numeric, get_inst(NLP_OR_CATEGORICAL_INST)"
    ),
    "NLP_OR_CATEGORICAL_INST": (
        "Decide if the current column generally suitable for NLP operations. Meaning, it is primarily multi word text entries, likely including many complete sentences.\n"
        "If the column is suitable for NLP operations, add the current column name to the encode_selections dictionary as NLP_Handler. END PROCESS.\n"
        "Otherwise, move on to get_inst(CATEGORICAL_1_INST)"
    ),
    "CATEGORICAL_1_INST": (
        "Decide if the current column contains Ordinal categories. Meaning, the feature's categories have a natural, meaningful order (e.g., skill levels, size categories, ratings, etc).\n"
        "Confirm the data has genuine ordinal semantics to be preserved in the numeric encoding.\n"
        "If the column is Ordinal, add the current column name to the encode_selections dictionary as Ordinal_Encode. END PROCESS."
        "Otherwise, move on to get_inst(CATEGORICAL_2_INST)"
    ),
    "CATEGORICAL_2_INST": (
        "Please review and confirm that this column is a reasonable candidate to be Numeric Label Encoded or One Hot Encoded.\n"
        "If column entries are of an unclear data type and or not possible canditades for Numeric Label Encoding or One Hot Encoding, add the current column name to the encode_selections dictionary as Failed_Encode_Selection and END PROCESS.\n"
        "Else, add the current column name to the encode_selections dictionary as Numeric_Encode and " # This is for Tree Based ML Models
        "add the current column name to the encode_selections dictionary as One_Hot_Encode.\n" # This is for Neural Network ML Models
        # IMPORTANT: Currently, all remaining features got to One_Hot_Encode_Categorical and are parsed by via Python with a mathematical threshold to Frequency_Count_Encoding.
        # FUTURE UPGRADE WANTED: Apply Domain Knowledge to Parse Between One_Hot vs. Frequency_Count Encoding at this LLM stage.
        "END PROCESS."
    ),
    #endregion
}

# encode_selections = {
#     'Numeric_Encode': [], # Tree Models Only
#     'One_Hot_Encode': [], # Neural Network Models Only
#     'Frequency_Count_Encode': [], # Future Feature (Not Currently Active)
#     'Ordinal_Encode': [],
#     'NLP_Handler':[],
#     'Scale_Or_Normalize': [],
#     'Encode_True_False_As_One_Zero': [],
#     'Failed_Encode_Selection': []
#     }   
