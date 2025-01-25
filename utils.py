
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
ANALYTICS = [
    (
        "ANALYTIC: there are duplicate rows in the data frame.\n" 
    ),
    (
        "ANALYTIC: there are spelling errors in the data frame.\n" 
    ),
    (
        "ANALYTIC: there are NULLS in the data frame .\n"
    )
]

ANALYTICS_INSTR = (
    "Your job is to create a list of tasks by analyzing a data using Python functions.\n"
    "You never complete tasks of alter the df. Your job is simply analyze data and to define tasks."
    "You will always utilize coding guidelines outlined in the get_coding_instructions tool.\n"
    "You will start by gaining a general semantic understanding of the data set.\n"  
    "Next you will iteratively create and deploy individual analyzation functions in order to generate information about the data set.\n"
    "As you iteratively generate information via new python functions, you will save appropriate 'Tasks' that need to be performed on the data.\n"
    "TOOLS: Use write_generated_func tool to save functions. Use exec_generated_func tool to execute functions on the df. Use add_task_to_list tool to save tasks.\n"
    "EXAMPLE: Create a Python function to check for nulls in the data set. If nulls are present, create a well defined task to be completed and save it using add_task_to_list.\n"
)

# OLD INSTRUCTIONS
# TASK_INST = (
#     "Use the steps below to complete the task.\n"
#     "1.) Use the coding_instructions tool to view guidelines to write a function to complete the task.\n"
#     "2.) Use the write_generated_func tool to create and save the new function.\n"
#     "3.) Use the exec_generated_func tool to apply the function to the data frame.\n"
#     "4.) If an error message is received from a tool, cease all operations and exit.\n"
# )

# NEW INSTRUCTIONS CREATE ANALYSIS FUNCTION TO CONFIRM TASK WAS COMPLETED
TASK_INST = (
    "Use the steps below to complete the task.\n"
    "1.) Use the get_coding_instructions tool to view guidelines to write a function to complete the task.\n"
    "2.) Use the write_generated_func tool to save the new function, and use the exec_generated_func tool to apply the function to the data frame.\n"
    "3.) Create a function to anlyze that data set and confirm the task has been completed.\n"
    "4.) Use the write_generated_func tool to save the new function, and use the exec_generated_func tool to apply the function to the data frame.\n"
    "5.) If the task is imcomplete, repeat steps 1 and 2.\n"
    "6.) If an error message is received from a tool, cease all operations and exit.\n"
)

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
#                                      Util Functions                                         #
#=============================================================================================#

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()
