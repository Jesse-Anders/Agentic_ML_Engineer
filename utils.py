from langchain_core.tools import tool

from agent_instructions.agent1_inst import AGENT1_IA
from agent_instructions.agent2_inst import AGENT2_IA
from agent_instructions.agent2_1_inst import AGENT2_1_IA
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
    "dataset_goal": "Disregard. Dataset goal not enetered.",
    "dataframe_stages": [],
    "nlp_columns": [],
    "agent3_1": None,
    "super_agent": None,
    "numeric_pow_groups": [],
    "object_pow_groups": [],
    "current_pow_group": [],
    "numeric_transform_columns": [],
    "ungrouped_cols": [],
    "skip_columns": [],
    "compare_col": None,
    "column_mappings": {},
    "redundancy_dictionary": {},
    'current_agent_name': None,
    'max_nlp_token_features': 1000,
    
    # Encode Assignment Dictionary: Used by agent 6 to assign columns for specific encoding actions for agent 7 
    "encode_selections": {
        'Numeric_Encode': [], # Tree Models Only
        'One_Hot_Encode': [], # Neural Network Models Only
        'Frequency_Count_Encode': [], # Future Feature (Not Currently Active)
        'Ordinal_Encode': [],
        'NLP_Handler':[],
        'Scale_Or_Normalize': [],
        'Failed_Encode_Selection': []
    }
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
    
def get_shared_var(var_name):
    if var_name in _shared_state:
        return _shared_state[var_name]
    raise Exception(f'Agent not found in _shared_state: {var_name}')
    
def set_shared_var(var_name, var):
    _shared_state[var_name] = var

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
from runtime_lib.static_agent_libs.agent2_1_static_lib import *
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