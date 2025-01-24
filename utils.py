
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


TASK_INST = (
    "Use the steps below to complete the task.\n"
    "1.) Use the coding_instructions tool to view guidelines for writing the function.\n"
    "2.) Use the write_generated_func tool to create and save the new function.\n"
    "3.) Use the exec_generated_func tool to apply the function to the data frame.\n"
    "4.) If an error message is received from a tool, cease all operations and exit.\n"
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
