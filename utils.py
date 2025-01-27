from langchain_core.tools import tool

#=============================================================================================#
#                                      STATIC GlOBALS                                         #
#=============================================================================================#

# directory path globals
DATA_INPUT_DIR = 'data_inputs'
DATA_OUTPUT_DIR = 'data_outputs'
LIB_DIR = 'runtime_lib'
SAVED_GENS_DIR = 'saved_generations'

JSON_DIR = 'json_lib'
STATIC_JSON_LIB = 'static_json_lib'
TASK_LIST = 'task_list'


# boilerplate file code
PIPELINE_BOILERPLATE = '''
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from pipeline_lib import *

'''

PIPELINE_LIB_BOILERPLATE = '''
# pipeline_lib.py

import pandas as pd

'''


#=============================================================================================#
#                                      PROMPT GlOBALS                                         #
#=============================================================================================#
# ANALYTICS = [
#     (
#         "ANALYTIC: there are duplicate rows in the data frame.\n" 
#     ),
#     (
#         "ANALYTIC: there are spelling errors in the data frame.\n" 
#     ),
#     (
#         "ANALYTIC: there are NULLS in the data frame .\n"
#     )
# ]

# ANALYTICS_INSTR = (
#     "Your job is to create a list of tasks by analyzing a data using Python functions.\n"
#     "You never complete tasks of alter the df. Your job is simply analyze data and to define tasks."
#     "You will always utilize coding guidelines outlined in the get_coding_instructions tool.\n"
#     "You will start by gaining a general semantic understanding of the data set.\n"  
#     "Next you will iteratively create and deploy individual analyzation functions in order to generate information about the data set.\n"
#     "As you iteratively generate information via new python functions, you will save appropriate 'Tasks' that need to be performed on the data.\n"
#     "TOOLS: Use write_generated_func tool to save functions. Use exec_generated_func tool to execute functions on the df. Use add_task_to_list tool to save tasks.\n"
#     "EXAMPLE: Create a Python function to check for nulls in the data set. If nulls are present, create a well defined task to be completed and save it using add_task_to_list.\n"
# )


# # NEW INSTRUCTIONS CREATE ANALYSIS FUNCTION TO CONFIRM TASK WAS COMPLETED
# TASK_INST = (
#     "Use the steps below to complete the task.\n"
#     "1.) Use the get_coding_instructions tool to view guidelines to write a function to complete the task.\n"
#     "2.) Use the write_generated_func tool to save the new function, and use the exec_generated_func tool to apply the function to the data frame.\n"
#     "3.) Create a function to anlyze that data set and confirm the task has been completed.\n"
#     "4.) Use the write_generated_func tool to save the new function, and use the exec_generated_func tool to apply the function to the data frame.\n"
#     "5.) If the task is imcomplete, repeat steps 1 and 2.\n"
#     "6.) If an error message is received from a tool, cease all operations and exit.\n"
# )

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

#=============================================================================================#
#  region                             Column Master Iteration Instructions                    #
#=============================================================================================#

def COLUMN_INST_START():
    return (
        "Use the exec_stored_func tool to run the data_type_check function to determine the Column's data type.\n"
        "State the column's data type.\n"
        "If data type is Integer, follow instructions in the IF_INT_INST tool.\n"
        "If data type is Float, follow instructions in the IF_FLOAT_INST tool.\n"
        "If data type is Object, follow instructions in the IF_OBJECT_INST tool.\n"
        "If data type is any other type, follow instructions in the IF_UNKNOWN_INST tool.\n"
        # f"If data type is Float, follow instructions: {IF_FLOAT_INST()}\n"
        # f"If data type is Object, follow instructions: {IF_OBJECT_INST()}\n"
        # f"If data type is any other type, follow instructions: {IF_UNKNOWN_INST()}\n"
    )

# endregion

#=============================================================================================#
#  region                              Column Type Integer Instructions                       #
#=============================================================================================#

@tool
def IF_INT_INST()-> str:
    """
    Instructions for handling Integer data type columns.
    """
    return (
    "Use exec_stored_func tool to run determine_numeric_or_categorical to determine if the column is truly numeric or if it is categroical.\n"
    "If returned column_type = numeric, use INT_NUMERIC_INST tool\n"
    "If returned column_type = categorical, use INT_CATEGORICAL_INST tool\n"
)


@tool
def INT_NUMERIC_INST()-> str:
    """
    Instructions for handling Numeric Integer columns.
    """
    return (
    "Use exec_stored_func tool to run check_outliers_and_nulls to find and describe outliers and or nulls \n"
    # "If Warnings are Present use exec_stored_func tool to run SOMETHING to record the issue!!\n"
    "If outliers AND OR nulls are present, use exec_stored_func tool to run cap_outliers_and_impute_nulls.\n"
)
@tool
def INT_CATEGORICAL_INST()-> str:
    """
    Instructions for handling Categorical Integer columns.
    """
    return (
    "Say that this integer column is categorical in nature"
    # "Use exec_stored_func tool to run is_null to detrmine if \n"
    # "If outliers are present, use exec_stored_func tool to run cap_outliers.\n"
    # f"If nulls are present, follow instructions: {INT_NULLS_INST()}\n"
)

#=============================================================================================#
#  region                              Column Type Float Instructions                         #
#=============================================================================================#
@tool
def IF_FLOAT_INST()-> str:
    """
    Instructions for handling Float data type columns.
    """
    return (
    "Use exec_stored_func tool to run if_float_is_really_int_convert.\n"
    "If column was 'converted to integer', run the IF_INT_INST tool\n"
    "If column 'remains as float', Use exec_stored_func tool to run determine_numeric_or_categorical to determine if the column is truly numeric or if it is categroical.\n"
    "If returned column_type = numeric, use FLOAT_NUMERIC_INST tool\n"
    "If returned column_type = categorical, use FLOAT_CATEGORICAL_INST tool\n"
)
@tool
def FLOAT_NUMERIC_INST()-> str:
    """
    Instructions for handling Numeric Float columns.
    """
    return (
    "Use exec_stored_func tool to run check_outliers_and_nulls to find and describe outliers and or nulls \n"
    # "If Warnings are Present use exec_stored_func tool to run SOMETHING to record the issue!!\n"
    "If outliers AND OR nulls are present, use exec_stored_func tool to run cap_outliers_and_impute_nulls.\n"
)
@tool
def FLOAT_CATEGORICAL_INST()-> str:
    """
    Instructions for handling Categorical Float columns.
    """
    return (
    "Say that this Float column is categorical in nature"
    # "Use exec_stored_func tool to run is_null to detrmine if \n"
    # "If outliers are present, use exec_stored_func tool to run cap_outliers.\n"
    # f"If nulls are present, follow instructions: {INT_NULLS_INST()}\n"
)

#=============================================================================================#
#  region                              Column Type Object Instructions                        #
#=============================================================================================#
@tool
def IF_OBJECT_INST()-> str:
    """
    Instructions for handling Object data type columns.
    """
    return (
    "Tell me you have read the Object instructions. And say Thank You. \n"
)

#=============================================================================================#
#  region                              Column Type Unknown Instructions                       #
#=============================================================================================#
@tool
def IF_UNKNOWN_INST()-> str:
    """
    Instructions for handling Unknown data type columns.
    """
    return (
    "Tell me you have read the Unknown instructions. And say Thank You. \n"
)


#=============================================================================================#
#                                      Util Functions                                         #
#=============================================================================================#

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

#=============================================================================================#
#                                      Agent Instruction @tool List                           #
#=============================================================================================#

instructions_list = [
    IF_INT_INST,
    INT_NUMERIC_INST,
    INT_CATEGORICAL_INST,
    IF_FLOAT_INST,
    FLOAT_NUMERIC_INST,
    FLOAT_CATEGORICAL_INST,
    IF_OBJECT_INST,
    IF_UNKNOWN_INST,
]