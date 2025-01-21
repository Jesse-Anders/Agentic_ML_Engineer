
#=============================================================================================#
#                                      STATIC GlOBALS                                         #
#=============================================================================================#

# directory path globals
DATA_INPUT_DIR = 'data_inputs'
DATA_OUTPUT_DIR = 'data_outputs'
LIB_DIR = 'lib'
PIPELINE_DIR = 'pipelines'
SAVED_GENS_DIR = 'saved_generations'


# boilerplate file code
PIPELINE_BOILERPLATE = '''
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from lib.static_lib import *
from lib.pipeline_lib import *

'''

PIPELINE_LIB_BOILERPLATE = '''
# pipeline_lib.py

'''


#=============================================================================================#
#                                      PROMPT GlOBALS                                         #
#=============================================================================================#

# Task List
TASKS = [
    (
        "TASK: Fix any spelling errors that exist in the rows of the df.\n"
        "First, use the search_lib tool to receive a list of all stored functions.\n"
        "If there is a function that fixes spelling errors, use the exec_stored_func tool to call it.\n"
        "If there isn't a function in the library that fixes spelling errors, use the write_generated_func tool to create one. The function's only parameter should be the df variable, no other parameters.\n"
        "The get_coding_instructions tool will provide you with the coding guidelines you are to follow.\n"
    ),
    (
        "TASK: Remove any duplicates from the df.\n"
        "First, use the search_lib tool to receive a list of all stored functions.\n"
        "If there is a function that removes duplicate rows, use the exec_stored_func tool to call it.\n"
        "If there isn't a function in the library that removes duplicate rows, use the write_generated_func tool to create one. The function's only parameter should be the df variable, no other parameters.\n"
        "The get_coding_instructions tool will provide you with the coding guidelines you are to follow.\n"
    )
]

# Coding Instructions / Guidelines / Constraints
CODE_INST = (
    "When writing new Python functions, follow these guidelines:\n"
    "- Ensure the function is Pythonic, efficient, and handles edge cases.\n"
    "- Include inline comments explaining the logic and any assumptions.\n"
    "- Test the function with realistic inputs to ensure correctness.\n"
    "- Use descriptive variable names to make the code readable.\n"
    "- Avoid hardcoding values; make the function reusable when possible.\n"
    "- Structure the code logically, with clear input and output specifications.\n"
    "- Employ textblob when handling spelling errors.\n"
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
