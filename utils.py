from langchain_core.tools import tool

#=============================================================================================#
#                                      STATIC GlOBALS                                         #
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


#=============================================================================================#
#                                      PROMPT GlOBALS                                         #
#=============================================================================================#


# Coding Instructions / Guidelines / Constraints
CODE_INST = (
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
)
#JESSE 1/21/25
# CURRENTLY NOT ACTIVE - Troubleshooting protocall for when LLM fails to write working code.
# Additionally, we will want to add a human in the loop bail out here.
CODE_INST_TROUBLESHOOTING = (
    "When LLM ENCOUNTERS ERRORS running the code on the first attempt...\n"
    "This can serve as a trouble shooting guide\n"
)

@tool
def get_coding_instructions() -> str:
    '''
    Provides detailed guidance for writing new python functions.
    Use this tool only when no pre-existing function meet the task requirements.
    '''
    return CODE_INST

#=============================================================================================#
#  region                        CAMEL :) Master START Iteration Instructions                 #
#=============================================================================================#

def CLEANING_AGENT1_START():
    return (
        "Use the exec_stored_func tool to run the data_type_check function to determine the Column's data type.\n"
        "State the column's data type.\n"
        "If data type is Float, follow instructions in the FLOAT_INST tool.\n"
        "If data type is Integer, follow instructions in the NUMERIC_INST tool.\n"
        "If data type is Object, follow instructions in the OBJECT_INST tool.\n"
        "If data type is any other type, follow instructions in the UNKNOWN_INST tool.\n"
    )

def OBJECT_TO_NUM_AND_ALIAS_NULLS_START():
    return (
        "Use the exec_stored_func tool to run the data_type_check function to determine the Column's data type.\n"
        "State the column's data type.\n"
        "If data type is Object, follow instructions in the OBJECT_TO_NUM_INST tool.\n"
        "If data type is any other type, END.\n"
    )

# endregion
#=============================================================================================#
#  region             OBJECT TO NUM AND ALIAS NULLS INSTRUCTIONS                              #
#=============================================================================================#

@tool
def OBJECT_TO_NUM_INST()-> str:
    """
    Instructions for finding Integer or Float cloumns that are currently Object data type columns.
    """
    return (
    "Use exec_stored_func tool to run check_percent_numeric to determine if the column is truly object or if it is numeric.\n"
    "If column 'is less than 90% numeric', use the HANDLE_COMMON_ALIAS_NULLS_IN_TEXT_COLUMN tool.\n"
    "If column 'is 90%+ numeric and can be considered truly numeric', use exec_stored_func tool to run check_for_text_nums.\n"
    "If result from check_for_text_nums comes back as True, use exec_stored_func to run convert_text_nums_to_numeric\n"
    "Continue on and follow instructions in the HANDLE_ALIAS_NULLS_IN_NUMS tool.\n"
    
)
@tool
def HANDLE_ALIAS_NULLS_IN_NUMS()-> str:
    """
    Instructions for handling mislabeled or alias nulls and remaining unidentifiable text to Null.
    """
    return (
    "Use exec_stored_func tool to run describe_and_clean_non_numeric_entries to find and covert mislabeled nulls to proper nulls.\n"
    "If 1 or more items added to the Unique Review List, use the exec_stored_func tool to run convert_all_non_num_to_null to convert all remaining text entries to proper nulls\n"
    "Use exec_stored_func tool to run convert_column_to_numeric. End Process\n"
)

@tool
def HANDLE_COMMON_ALIAS_NULLS_IN_TEXT_COLUMN()-> str:
    """
    Instructions for handling common mislabeled or alias nulls, like empty, unknown, none, etc in standard object type/text .
    """
    return (
    "Use exec_stored_func tool to run convert_common_alias_nulls to find and convert mislabeled nulls to proper nulls.\n"
    "Continue on and follow instructions in the HANDLE_UNCOMMON_ALIAS_NULLS_IN_TEXT_COLUMN tool.\n"
)

@tool
def HANDLE_UNCOMMON_ALIAS_NULLS_IN_TEXT_COLUMN()-> str:
    """
    Instructions for handling uncommon mislabeled or alias nulls, using LLM logic .
    """
    return (
    "Use exec_stored_func tool to run display_most_common_unique_entries and review the most common unique entries in the column.\n"
    "Look through the unique entries and try to determine if there are any entries that should be nulls, meaning they are 'very likely mislabeled nulls'.\n"
    "If any exist, use the JSON_LIST_INSTRUCTIONS tool to format your list of 'very likely mislabeled nulls' and use the add_nulls_to_list tool to save the list.\n"
    # IMPORTANT: We need a way to send this json list (in this state) to the pipeline.
    "If you added mislabeled nulls to the list, use the exec_stored_func tool to run convert_uncommon_alias_nulls to convert items in the list to nulls.\n"
    "If you found no 'very likely mislabeled nulls'. End Process\n"

)

@tool
def JSON_LIST_INSTRUCTIONS() -> str:
    """
    Instructions for creating a well-formatted JSON list of alias nulls.
    """
    return (
        "Here is a simple example of a well-formatted JSON list:\n"
        '[ "na", "missing", "none", "unknown", "empty" ]\n'
        "Ensure that:\n"
        "1. Each entry is a string enclosed in double quotes.\n"
        "2. Entries are separated by commas.\n"
        "3. No trailing commas after the last item.\n"
        "4. The list should not contain any extra characters, comments, or notes.\n"
        "5. The list must be valid JSON format.\n\n"

    )

# endregion
#=============================================================================================#
#  region                  Column Type Integer Instructions                                   #
#=============================================================================================#
@tool
def FLOAT_INST()-> str:
    """
    Instructions for handling Float data type columns.
    """
    return (
    "Use exec_stored_func tool to run if_float_is_really_int_convert.\n"
    "Follow instructions in the NUMERIC_INST tool.\n"

)

@tool
def NUMERIC_INST()-> str:
    """
    Instructions for handling Integer data type columns.
    """
    return (
    "Use exec_stored_func tool to run determine_numeric_or_categorical to determine if the column is truly numeric or if it is categroical.\n"
    "If returned column_type = numeric, use NUMERIC_NULL_AND_OUTLIER_INST tool\n"
    "If returned column_type = categorical, use CATEGORICAL_NULL_AND_OUTLIER_INST tool\n"
)

@tool
def NUMERIC_NULL_AND_OUTLIER_INST()-> str:
    """
    Instructions for handling numeric columns.
    """
    return (
    "Use exec_stored_func tool to run check_outliers_and_nulls to find and describe outliers and or nulls \n"
    # "If Warnings are Present use exec_stored_func tool to run SOMETHING to record the issue for human review!!\n"
    "If outliers AND OR nulls are present, use exec_stored_func tool to run cap_outliers_and_impute_nulls.\n"
)

@tool
def CATEGORICAL_NULL_AND_OUTLIER_INST()-> str:
    """
    Instructions for handling Categorical numeric columns.
    """
    return (
    "Say that this integer column is categorical in nature. \n"
        #THESE ARE IN PROCESS - Jesse 1/27/25
    #"Use exec_stored_func tool to run SOMETHING ABOUT CATEGORIES to work with \n"
    #"If nulls are present, Use exec_stored_func tool to run impute_mode_or_create_exnulls_cat \n"
)

# endregion
#=============================================================================================#
#  region                              Column Type Object Instructions                        #
#=============================================================================================#
@tool
def OBJECT_INST()-> str:
    """
    Instructions for handling Object data type columns.
    """
    return (
    "Tell me you have read the Object instructions. And say Thank You. \n"
)
# endregion
#=============================================================================================#
#  region                              Column Type Unknown Instructions                       #
#=============================================================================================#
@tool
def UNKNOWN_INST()-> str:
    """
    Instructions for handling Unknown data type columns.
    """
    return (
    "Tell me you have read the Unknown instructions. And say Thank You. \n"
)

#endregion
#=============================================================================================#
#  region                                    Util Functions                                   #
#=============================================================================================#

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()
# endregion
#=============================================================================================#
#  region                                    Agent Instruction @tool List                     #
#=============================================================================================#

instructions_list = [
    # Agent is OJECT_TO_NUM_AND_ALIAS_NULLS
    OBJECT_TO_NUM_INST,
    HANDLE_ALIAS_NULLS_IN_NUMS,
    HANDLE_COMMON_ALIAS_NULLS_IN_TEXT_COLUMN,
    HANDLE_UNCOMMON_ALIAS_NULLS_IN_TEXT_COLUMN,
    JSON_LIST_INSTRUCTIONS,
    # Agent is CLEANING_AGENT1 
    FLOAT_INST,
    NUMERIC_INST,
    NUMERIC_NULL_AND_OUTLIER_INST,
    CATEGORICAL_NULL_AND_OUTLIER_INST,
    OBJECT_INST,
    UNKNOWN_INST,
]
# endregion