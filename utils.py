from langchain_core.tools import tool

#=============================================================================================#
#  region                              STATIC GlOBALS                                         #
#=============================================================================================#

# directory path globals
DATA_INPUT_DIR = 'data_inputs'
DATA_OUTPUT_DIR = 'data_outputs'
LIB_DIR = 'runtime_lib'
SAVED_GENS_DIR = 'saved_generations'

# JSON
JSON_DIR = 'json_lib'
STATIC_JSON_LIB = 'static_json_lib'
TASK_LIST = 'task_list'
ALIAS_NULLS_PATH = "json_lib/alias_nulls_list.json"

# boilerplate file code
PIPELINE_BOILERPLATE = '''
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from static_lib import *
from pipeline_lib import *

'''

PIPELINE_LIB_BOILERPLATE = '''
# pipeline_lib.py

import pandas as pd

'''

#  endregion  ================================================================================#
#  region                              UTIL FUNCTIONS                                         #
#=============================================================================================#

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

#  endregion  ================================================================================#
#  region                              INSTRUCTION ARCHIVE                                    #
#=============================================================================================#


INST_ARCHIVE = {
#  endregion  ================================================================================#
#    region                            CODING INSTRUCTIONS                                    #
#=============================================================================================#
    "CODE_INST": (
        "When writing new Python functions, follow these guidelines:\n"
        "- Ensure the function is Pythonic, efficient, and handles edge cases.\n"
        "- Be sure that all expected arguments in the function already exist in the task.\n"
        "- WARNING EXAMPLE: Functions cannot be applied to a specific column (argument) if there are no columns listed in the task.\n"
        "- Include inline comments explaining the logic and any assumptions.\n"
        "- Test the function with realistic inputs to ensure correctness.\n"
        "- Use descriptive variable names to make the code readable.\n"
        "- Avoid hardcoding values; make the function reusable when possible.\n"
        "- Structure the code logically, with clear input and output specifications.\n"
        "- Employ textblob when handling spelling errors.\n"
    ),
    # JESSE 1/21/25: CURRENTLY NOT ACTIVE - Troubleshooting protocall for when LLM fails to write working code.
    # Additionally, we will want to add a human in the loop bail out here.
    "CODE_INST_TROUBLESHOOTING": (
        "When LLM ENCOUNTERS ERRORS running the code on the first attempt...\n"
        "This can serve as a trouble shooting guide\n"
    ),
#    endregion  ==============================================================================#
#    region                            CAMEL CARAVAN :) Master START Iteration Instructions   #
#=============================================================================================#
    "OBJECT_TO_NUM_AND_ALIAS_NULLS_START": (
        "Use the exec_stored_func tool to run the data_type_check function to determine the Column's data type.\n"
        "State the column's data type.\n"
        "If data type is Object, use the tool call get_inst(OBJECT_TO_NUM_INST) for instructions.\n"
        "If data type is any other type, END.\n"
    ),
    "CLEANING_AGENT1_START": (
        "Use the exec_stored_func tool to run the data_type_check function to determine the Column's data type.\n"
        "State the column's data type.\n"
        "If data type is Float, use the tool call get_inst(FLOAT_INST) for instructions.\n"
        "If data type is Integer, use the tool call get_inst(NUMERIC_INST) for instructions.\n"
        "If data type is Object, use the tool call get_inst(OBJECT_INST) for instructions.\n"
        "If data type is any other type, use the tool call get_inst(UNKNOWN_INST) for instructions.\n"
    ),
#    endregion  ==============================================================================#
#    region                            OBJECT TO NUM AND ALIAS NULLS INSTRUCTIONS             #
#=============================================================================================#
    # Instructions for finding Integer or Float cloumns that are currently Object data type columns.
    "OBJECT_TO_NUM_INST": (
        "Use exec_stored_func tool to run check_percent_numeric to determine if the column is truly object or if it is numeric.\n"
        "If column 'is less than 90% numeric', use the tool call get_inst(HANDLE_COMMON_ALIAS_NULLS_IN_TEXT_COLUMN) for instructions.\n"
        "If column 'is 90%+ numeric and can be considered truly numeric', use exec_stored_func tool to run check_for_text_nums.\n"
        "If the result from check_for_text_nums comes back as True, use exec_stored_func to run convert_text_nums_to_numeric\n"
        "Continue on by using the tool call get_inst(HANDLE_ALIAS_NULLS_IN_NUMS) for instructions.\n"
    ), # Instructions for handling mislabeled or alias nulls and remaining unidentifiable text to Null.
    "HANDLE_ALIAS_NULLS_IN_NUMS": (
        "Use exec_stored_func tool to run describe_and_clean_non_numeric_entries to find and covert mislabeled nulls to proper nulls.\n"
        "If 1 or more items added to the Unique Review List, use the exec_stored_func tool to run convert_all_non_num_to_null to convert all remaining text entries to proper nulls\n"
        "Use exec_stored_func tool to run convert_column_to_numeric. END PROCESS\n"
    ), # Instructions for handling common mislabeled or alias nulls, like empty, unknown, none, etc in standard object type/text.
    "HANDLE_COMMON_ALIAS_NULLS_IN_TEXT_COLUMN": (
        "Use exec_stored_func tool to run convert_common_alias_nulls to find and convert mislabeled nulls to proper nulls.\n"
        "Continue on by using the tool call get_inst(HANDLE_UNCOMMON_ALIAS_NULLS_IN_TEXT_COLUMN) for instructions.\n"
    ), # Instructions for handling uncommon mislabeled or alias nulls, using LLM logic.
    "HANDLE_UNCOMMON_ALIAS_NULLS_IN_TEXT_COLUMN": (
        "Use exec_stored_func tool to run display_most_common_unique_entries and review the most common unique entries in the column.\n"
        "Look through the unique entries and try to determine if there are any entries that should be nulls, meaning they are 'very likely mislabeled nulls'.\n"
        "If any exist, call get_inst(JSON_LIST_INST) for instructions on formatting a list of 'very likely mislabeled nulls' and use the add_nulls_to_list tool to save the new list.\n"
        # IMPORTANT: We need a way to send this json list (in this state) to the pipeline.
        "If you added mislabeled nulls to the list, use the exec_stored_func tool to run convert_uncommon_alias_nulls to convert items in the list to nulls.\n"
        "If you found no 'very likely mislabeled nulls'. End Process\n"
    ), # Instructions for creating a well-formatted JSON list of alias nulls.
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
#    endregion  ==============================================================================#
#    region                            COLUMN TYPE INTEGER INSTRUCTIONS                       #
#=============================================================================================#
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
        "Use exec_stored_func tool to run check_outliers_and_nulls to find and describe outliers and or nulls \n"
        # "If Warnings are Present use exec_stored_func tool to run SOMETHING to record the issue for human review!!\n"
        "If outliers AND OR nulls are present, use exec_stored_func tool to run cap_outliers_and_impute_nulls.\n"
    ), # Instructions for handling Categorical numeric columns.
    "CATEGORICAL_NULL_AND_OUTLIER_INST": (
        "Say that this integer column is categorical in nature. \n"
            #THESE ARE IN PROCESS - Jesse 1/27/25
        #"Use exec_stored_func tool to run SOMETHING ABOUT CATEGORIES to work with \n"
        #"If nulls are present, Use exec_stored_func tool to run impute_mode_or_create_exnulls_cat \n"
    ),
#    endregion  ==============================================================================#
#    region                            COLUMN TYPE OBJECT INSTRUCTIONS                        #
#=============================================================================================#
    # Instructions for handling Object data type columns.
    "OBJECT_INST": (
        "Tell me you have read the Object instructions. And say Thank You. \n"
    ),
#    endregion  ==============================================================================#
#    region                            COLUMN TYPE UNKNOWN INSTRUCTIONS                       #
#=============================================================================================#
    # Instructions for handling Unknown data type columns.
    "UNKNOWN_INST": (
        "Tell me you have read the Unknown instructions. And say Thank You. \n"
    )
} #endregion