AGENT1_IA = {
#=============================================================================================#
#    region          AGENT 1           OBJECT TO NUM AND ALIAS NULLS INSTRUCTIONS             #
#=============================================================================================#
    
# AGENT1 Kickoff Instructions (Evaluate if High Null Percentage Dictates Column Drop)
    "AGENT1_START": (
        "Use exec_stored_func tool to run evaluate_column_for_drop(df) to deternime if the column should be dropped.\n"
        "If recommended_action is 'drop', exec_stored_func to run drop_column(df) to drop the column from the df. END PROCESS.\n"
        "If recommended_action is 'keep' use the exec_stored_func to run data_type_check(df).\n"
        "If data type is 'object' call tool get_inst(CONFIRM_TRULY_OBJECT) for further instructions.\n"
        "If data type is not 'object', END PROCESS.\n"
    ), 
# Confirms that the column data type is truly text and not a truly numeric column with sparse text items.
    "CONFIRM_TRULY_OBJECT": (
        "Use exec_stored_func tool to run check_percent_numeric(df) to determine if the column is truly object or if it is numeric.\n"
        "If column 'is less than 90% numeric', use the tool call get_inst(HANDLE_ALIAS_NULLS_IN_TEXT) for instructions.\n"
        "If column 'is 90%+ numeric and can be considered truly numeric', use exec_stored_func tool to run check_for_text_nums(df).\n"
        "If the result from check_for_text_nums comes back as True, use exec_stored_func to run convert_text_nums_to_numeric(df).\n"
        "Continue on by using the tool call get_inst(HANDLE_ALIAS_NULLS_IN_NUMS) for instructions.\n"
    ),
# Instructions for handling mislabeled or alias nulls and remaining unidentifiable text to Null.
    "HANDLE_ALIAS_NULLS_IN_NUMS": (
        "Use exec_stored_func tool to run describe_and_clean_non_numeric_entries(df) to find and convert mislabeled nulls to proper nulls.\n"
        "If 1 or more items added to the Unique Review List, use the exec_stored_func tool to run convert_all_non_num_to_null(df) to convert all remaining text entries to proper nulls\n"
        "Use exec_stored_func tool to run convert_column_to_numeric(df). END PROCESS\n"
    ), 
# Instructions for handling common mislabeled or alias nulls, like empty, unknown, none, etc in standard object type/text.
    "HANDLE_ALIAS_NULLS_IN_TEXT": (
        "Use exec_stored_func tool to run convert_common_alias_nulls(df) to find and convert mislabeled nulls to proper nulls.\n"
        "Continue on by using the tool call get_inst(HANDLE_ALIAS_NULLS_IN_TEXT_LLM) for instructions.\n"
    ), 
# Instructions for handling uncommon mislabeled or alias nulls, using LLM logic.
    "HANDLE_ALIAS_NULLS_IN_TEXT_LLM": (
        "Use exec_stored_func tool to run display_most_common_unique_entries(df) and review the most common unique entries in the column.\n"
        "Look through the unique entries and try to determine if there are any entries that should be nulls, meaning they are 'very likely mislabeled nulls'.\n"
        "If any exist, call get_inst(JSON_LIST_INST) for instructions on formatting a list of 'very likely mislabeled nulls' and use the append_to_json_list tool with json_path as 'json_lib/alias_nulls_list.json' to save the new list.\n"
        # IMPORTANT: We need a way to send this json list (in this state) to the pipeline.
        "If you added mislabeled nulls to the list, use the exec_stored_func tool to run convert_uncommon_alias_nulls(df) to convert items in the list to nulls, then End Process.\n"
        "If you found no 'very likely mislabeled nulls'. END PROCESS\n"
    ), 
# Instructions for creating a well-formatted JSON list of alias nulls.
    "JSON_LIST_INST": (
        "Here is a simple example of a well-formatted JSON list:\n"
        '[ "na", "missing", "none", "unknown", "empty" ]\n'
        "Ensure that:\n"
        "1. Each entry is a string enclosed in double quotes.\n"
        "2. Entries are separated by commas.\n"
        "3. No trailing commas after the last item.\n"
        "4. The list should not contain any extra characters, comments, or notes.\n"
        "5. The list must be valid JSON format.\n\n"
    ),
    
}