from langchain_core.tools import tool

from agent_instructions.agent1_inst import AGENT1_IA
from agent_instructions.agent2_inst import AGENT2_IA
from agent_instructions.agent3_inst import AGENT3_IA
from agent_instructions.agent4_inst import AGENT4_IA
from agent_instructions.agent5_inst import AGENT5_IA
from agent_instructions.agent6_inst import AGENT6_IA


#=============================================================================================#
#  region                              Shared State Globals                                   #
#=============================================================================================#

_shared_state = {
    "current_column": None,
    "target_column": None,
    "dataframe_stages": [],
    "nlp_columns": [],
    "agent3_1": None
}

PIPELINE_WRITE_LIST = [ # They're in chronological order (agent1_static_lib funcs, agent2_static_lib funcs...)
    "drop_column",
    "convert_text_nums_to_numeric",
    "convert_column_to_numeric",
    "convert_common_alias_nulls",
    "convert_uncommon_alias_nulls",
    "winsorize_column",
    "log_transform_column",
    "knn_impute_with_rounding",
    "dynamic_stochastic_median_impute",
    "convert_nulls_to_category",
    "impute_categorical_numeric_mode"
]

#  endregion  ================================================================================#
#  region                                Shared State Handling                                #
#=============================================================================================#

def get_dataframe_stage(stage_name):
    for stage in _shared_state["dataframe_stages"]:
        if stage['stage_name'] == stage_name:
            return stage['df']
    raise Exception(f"A dataframe stage does not exist with this stage_name: {stage_name}")

def save_dataframe_stage(df, stage_name):
    for stage in _shared_state["dataframe_stages"]:
        if stage_name == stage['stage_name']:
            stage['df'] = df
            return
    _shared_state["dataframe_stages"].append({
        "stage_name": stage_name,
        "df": df.copy()
    })

def get_current_column():
    return _shared_state["current_column"]

def set_current_column(column):
    _shared_state["current_column"] = column

def get_target_column():
    return _shared_state["target_column"]

def set_target_column(column):
    _shared_state["target_column"] = column

def get_nlp_columns():
    return _shared_state["nlp_columns"]

def add_nlp_column(column):
    _shared_state["nlp_columns"].append(column)

def get_agent3_1():
    return _shared_state["agent3_1"]

def set_agent3_1(agent):
    _shared_state["agent3_1"] = agent

def get_super_agent():
    return _shared_state["super_agent"]

def set_super_agent(agent):
    _shared_state["super_agent"] = agent

# TODO: Centralied agent getter & setter
# def get_agent(agent_name):
# def set_agent(agent_name, agent):
#     if agent_name doesn't exist:
#       create a new one

#  endregion  ================================================================================#
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
# generated_pipeline

# This file is intended to be a reusable data pipeline.

import pandas as pd, sys, os

from static_lib import *
from pipeline_lib import *

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from utils import set_current_column
from runtime_lib.static_agent_libs.agent1_static_lib import *
from runtime_lib.static_agent_libs.agent2_static_lib import *
from runtime_lib.static_agent_libs.agent3_static_lib import *
from runtime_lib.static_agent_libs.agent4_static_lib import *
from runtime_lib.static_agent_libs.agent5_static_lib import *
from runtime_lib.static_agent_libs.agent6_static_lib import *

# SYSTEM GENERATION START:

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

    "HANDWASHING_AGENT_START": (
        "Tell me that you have successfully handwashed the data. END.\n"
    ),


# endregion

} 