import argparse
import ast
import importlib
import json
import os
import re
import pandas as pd
import shutil

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from openai import OpenAI
from typing import Annotated

from utils import *
from runtime_lib.static_lib import *

from runtime_lib.static_agent_libs.agent1_static_lib import *
from runtime_lib.static_agent_libs.agent2_static_lib import *
from runtime_lib.static_agent_libs.agent3_static_lib import *
from runtime_lib.static_agent_libs.agent4_static_lib import *
from runtime_lib.static_agent_libs.agent5_static_lib import *
from runtime_lib.static_agent_libs.agent6_static_lib import *

import runtime_lib.static_agent_libs.agent1_static_lib as agent1
import runtime_lib.static_agent_libs.agent2_static_lib as agent2
import runtime_lib.static_agent_libs.agent3_static_lib as agent3
import runtime_lib.static_agent_libs.agent4_static_lib as agent4
import runtime_lib.static_agent_libs.agent5_static_lib as agent5
import runtime_lib.static_agent_libs.agent6_static_lib as agent6

# List of agent modules
AGENT_MODULES = [agent1, agent2, agent3, agent4, agent5, agent6]

# INSTRUCTION ARCHIVE LIST: Used in the get_inst tool
IA_LIST = [INST_ARCHIVE, AGENT1_IA, AGENT2_IA, AGENT3_IA, AGENT4_IA, AGENT5_IA, AGENT6_IA]

#=============================================================================================#
#  region                                Dynamic Globals                                      #
#=============================================================================================#

# PyFile objects for managing each individual code library / pipeline
static_lib = None
pipeline_lib = None
sandbox = None
pipeline = None

# Preprocessor and FeatureEngineer objects for global ML Workflow
preprocessor = None
feature_engineer = None

#  endregion  ================================================================================#
#  region                                OpenAI API                                           #
#=============================================================================================#

try:
    load_dotenv()
except Exception as e:
    print(f'Error loading dotenv: {e}')

# OpenAI Access
def get_openai_api_key():
    try:
        return os.getenv("OPENAI_API_KEY")
    except Exception as e:
        print(f'Error retrieving OpenAI API Key: {e}')

#  endregion  ================================================================================#
#  region                                LM Studio API                                        #
#=============================================================================================#

lms_client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")


def get_lmstudio_response(model, msg_list, temperature=0.7, stream=False):
    '''
    Sends a chat completion request to an LM Studio server and retrieves the generated response.

    model (str): The name of the LM Studio model to use for generating responses.
    msg_list (list): A list of dictionaries representing the conversation history.
    temperature (float, optional): The sampling temperature to use for response generation.
    stream (bool, optional): Whether to enable streaming of the response.
    '''
    try:
        completion = lms_client.chat.completions.create(
            model=model,
            messages=msg_list,
            temperature=temperature,
            stream=stream
        )

    except Exception as e:
        print(f'Error during LLM completion request: {e}')
        return

    response = ''
    
    for chunk in completion:
        if chunk.choices[0].delta.content:
            response += chunk.choices[0].delta.content

    return response

#  endregion  ================================================================================#
#  region                                PyFile                                               #
#=============================================================================================#

class PyFile:
    '''
    A container class for managing the various python files being updated by the react agent.
    All logic for performing operations on the library files, sandbox file, and pipeline file
    should be here.
    '''
    def __init__(self, path, args):
        self.path = path
        self.args = args
        
        # string representation of the file
        self.content = self.read()

    def get_func(self, func_name):
        '''
        Returns the function object matching the given name

        func_name: name of the function to be returned
        '''
        try:
            for module in AGENT_MODULES:
                if hasattr(module, func_name):
                    return getattr(module, func_name)
            print(f"Function '{func_name}' not found in any module.")
            return -1
        except Exception as e:
            print(f'Error loading function: {e}')
            return -1  # Error code to be caught within tool functions

    def get_func_objects(self):
        '''
        Returns a JSON string of all function names and descriptions.
        '''
        try:
            with open(self.path, 'r') as file:
                tree = ast.parse(file.read())
        except Exception as e:
            print(f'Error parsing PyFile: {e}')

        func_list = []

        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    description_value = ''

                    docstring = ast.get_docstring(node)
                    if docstring:

                        # this is the key that all static functions should contain
                        description_key = '[description]:'
                        
                        for line in docstring.split('\n'):
                            line = line.strip()
                            if line.startswith(description_key):
                                description_value = line.split(':', maxsplit=1)[1].strip()
                                break

                    func_list.append({
                        'function_name': func_name,
                        'description': description_value
                    })

            return func_list

        except Exception as e:
            print(f'Error extracting function list from libraries: {e}')
            return

    def read(self):
        '''
        Return a string of the code
        '''
        try:
            content = open(self.path, 'r').read()
            self.content = content
            return content
        except Exception as e:
            print(f'Error reading PyFile: {e}')

    def read_imports(self):
        '''
        Returns a list of code string lines that contain import statements in the file
        '''
        self.read()
        lines = self.content.split('\n')

        # extract import lines with no inline comments
        import_lines = [line for line in lines if 'import' in line and '#' not in line]

        return import_lines
    
    def reset(self):
        '''
        Wipes all content from the file
        '''
        try:
            with open(self.path, 'w') as file:
                file.write('')
            self.read()
        except Exception as e:
            print(f'Error resetting PyFile: {e}')
    
    def write(self, code_string):
        '''
        Appends a given string of code to the file
        
        code_string: string of code to append
        '''
        try:
            self.read()

            # get list of current imports
            current_imports = self.read_imports()
            
            # remove any duplicate import statements from the code_string
            lines = code_string.split('\n')
            import_lines = [line for line in lines if 'import' in line and '#' not in line]
            duplicate_imports = [line for line in import_lines if line in current_imports]
            lines = [line for line in lines if line not in duplicate_imports]

            # write the code to file
            self.content += '\n'.join(lines) + '\n'
            with open(self.path, 'w') as file:
                file.write(self.content)

        except Exception as e:
            print(f'Error writing to PyFile (PyFile.write): {e}')

#  endregion  ================================================================================#
#  region                                Tool Functions                                       #
#=============================================================================================#

@tool
def get_inst(
    inst_key: Annotated[str, 'name of the instruction set being retrieved']
) -> str:
    '''
    Returns the instructions paired to the given inst_key instruction set key.

    inst_key: the exact name of the set (examples: "CODE_INST", "CLEANING_AGENT2_START", "OBJECT_INST", etc.)
    '''
    for instruction_set in IA_LIST:
        if inst_key in instruction_set:
            return instruction_set[inst_key]
    return f'Error: Cannot find instruction set {inst_key}'

@tool
def logger(
    message: Annotated[str, 'the message, warning, or error to be logged in the pipeline file']
) -> str:
    '''
    Uses comments to document a message in the pipeline.py file
    '''
    try:
        if message.strip()[0] != '#':
            message = '# ' + message
        pipeline.write(message)
        return f'LOGGED Message: {message}'
    except Exception as e:
        return f'Error logging message: {e}'
    
@tool
def write_generated_func(
    code: Annotated[str, 'string of the code being written to the sandbox.py file']
) -> str:
    '''
    Writes the given code to the sandbox.
    '''
    sandbox.reset() # clear any leftover output

    try:
        sandbox.write(code + '\n')
        return 'Successfully added function to the sandbox'
    except Exception as e:
        return f'Error writing generated function: {e}'

@tool
def exec_stored_func(
    func_call_code: Annotated[str, '''The line of code to call the function. Only include the df parameter unless instructed otherwise.
                              Always write "output = " before the function call to catch return values. Format example: output = func_name(df)''']
) -> str:
    '''
    Executes a static function on the current working dataframe and writes the function call to the pipeline file.
    '''

    # Extracting the function name using regex
    match = re.search(r'output\s*=\s*(\w+)\s*\(', func_call_code)
    if not match:
        return 'Error: Could not extract function name from the provided code.'
    
    func_name = match.group(1)

    print(f"Agent is attempting to run {func_name} on the '{get_current_column()}' column")

    try:
        func = static_lib.get_func(func_name)
    except Exception as e:
        return f'Error loading function from file: {e}'

    if func == -1 or func == None: # -1 is the error code from lib.get_func
        return f'Function is None[{func}] and could not be retrieved'
        
    try:
        # Dynamically execute the function call code
        df = preprocessor.get_df() if preprocessor.active else feature_engineer.get_df()
        local_vars = {'df': df}
        exec(func_call_code, globals(), local_vars)

        # Capture the updated DataFrame (if any)
        output = local_vars.get('output', None)

        # Update the preprocessor's DataFrame if the function modifies it in place or returns it
        updated_df = output if isinstance(output, pd.DataFrame) else local_vars.get('df', None)
        if isinstance(updated_df, pd.DataFrame):
            if preprocessor.active:
                preprocessor.update_df(updated_df)
            elif feature_engineer.active:
                feature_engineer.update_df(updated_df)
        else:
            print('Error updating local dataframe')
    except Exception as e:
        return f'Error executing function locally: {e}'

    try:
        # Write the function call code to the pipeline file if it makes changes to the df
        if func_name in PIPELINE_WRITE_LIST:
            if func_call_code[:8] == 'output =':
                func_call_code = 'df =' + func_call_code[8:]

            pipeline.write(func_call_code)

        return f'Successfully executed function: {func_name}\n\nFunction Output: {output if not isinstance(output, pd.DataFrame) else "[UPDATED DF]"}'
    except Exception as e:
        return f'Error writing function call to pipeline: {e}'

@tool
def exec_generated_func(
    func_call_code: Annotated[str, '''The line of code to call the sandbox function. Include necessary parameters and values except for the 'df' parameter which will be passed in locally.
                              Always write "output = " before the function call to catch return values. Format example: output = func_name(df)''']
) -> str:
    '''
    Executes a sandbox function on the current working dataframe and writes the function call to the pipeline file.
    '''

    # Extracting the function name using regex
    match = re.search(r'output\s*=\s*(\w+)\s*\(', func_call_code)
    if not match:
        return 'Error: Could not extract function name from the provided code.'
    
    func_name = match.group(1)

    print(f"Agent is attempting to run {func_name} on the '{get_current_column()}' column")

    try:
        # Get the function code from the sandbox
        func_code = sandbox.read()

        # Dynamically define the function in the local context
        exec(func_code, globals())
        func = globals().get(func_name)

        if func is None:
            raise ValueError(f'Function {func_name} could not be defined.')
    except Exception as e:
        return f'Error loading function from sandbox: {e}'

    try:
        # Dynamically execute the function call code
        df = preprocessor.get_df() if preprocessor.active else feature_engineer.get_df()
        local_vars = {'df': df}
        exec(func_call_code, globals(), local_vars)

        # Capture the updated DataFrame (if any)
        output = local_vars.get('output', None)

        # Update the preprocessor's DataFrame if the function modifies it in place or returns it
        updated_df = output if isinstance(output, pd.DataFrame) else local_vars.get('df', None)
        if isinstance(updated_df, pd.DataFrame):
            if preprocessor.active:
                preprocessor.update_df(updated_df)
            elif feature_engineer.active:
                feature_engineer.update_df(updated_df)
        else:
            print('Error updating local dataframe')
    except Exception as e:
        return f'Error executing function locally: {e}'

    try:
        # Write the function call code to the pipeline file if it makes changes to the df
        if func_call_code[:8] == 'output =':
            func_call_code = 'df =' + func_call_code[8:]
        pipeline.write(func_call_code)

        # Save the function code from the sandbox to the pipeline_lib
        pipeline_lib.write(func_code)
        sandbox.reset()

        return f'Successfully executed and saved function: {func_name}'
    except Exception as e:
        return f'Error writing function call to pipeline: {e}'

@tool
def append_alias_nulls(
    new_nulls: Annotated[list, 'the list of mislabeled nulls to be added to the alias null list.']
) -> str:
    '''
    Appends new alias nulls to the existing list in the JSON file.
    If the file doesn't exist or is empty, it will initialize with an empty list.

    Example JSON structure:
    ["na", "missing", "none", "unknown", "empty"]
    '''
    try:
        # Ensure the input is a list of strings
        if not isinstance(new_nulls, list):
            return "Error: The provided data is not a list."
        if not all(isinstance(item, str) for item in new_nulls):
            return "Error: All items in the list must be strings."

        # Initialize the JSON file with an empty list if it doesn't exist or is empty
        if not os.path.exists(ALIAS_NULLS_PATH) or os.path.getsize(ALIAS_NULLS_PATH) == 0:
            with open(ALIAS_NULLS_PATH, "w") as file:
                json.dump([], file, indent=4)  # Initialize with an empty list
            print(f"Initialized empty JSON file at {ALIAS_NULLS_PATH}.")

        # Load the existing null list from the JSON file
        with open(ALIAS_NULLS_PATH, "r") as file:
            null_list = json.load(file)

        # Append the new nulls to the existing list and remove duplicates
        null_list.extend(new_nulls)
        null_list = list(set(null_list))

        # Save the updated null list back to the JSON file
        with open(ALIAS_NULLS_PATH, "w") as file:
            json.dump(null_list, file, indent=4)

        return f"Nulls successfully added: {new_nulls}"

    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool
def add_nlp_column(
    column: Annotated[str, 'the name of the NLP column being added.']
) -> str:
    '''
    Appends a new NLP column to the global list of NLP columns.
    '''
    if column not in get_nlp_columns:
        add_nlp_column(column)
        return(f'Successfully add column to NLP columns: {column}')
    return(f'Column already in NLP columns: {column}')

tools = [
    get_inst,
    logger,
    exec_stored_func,
    append_alias_nulls,
    add_nlp_column
]


#  endregion  ================================================================================#
#  region                                Preprocessor                                         #
#=============================================================================================#

class Preprocesser:
    def __init__(self, args, df):
        self.args = args
        self.active = False

        self.original_df = df.copy()
        self.backup_df = df.copy()
        self.df = df.copy()

    def get_df(self):
        '''
        Return current df
        '''
        return self.df
    
    def set_df(self, df):
        '''
        Reassigns all dataframe variables
        '''
        self.original_df = df.copy()
        self.backup_df = df.copy()
        self.df = df.copy()

    def restore_backup_df(self):
        '''
        Rolls the working dataframe back to its last saved version
        '''
        self.df = self.backup_df.copy()

    def run(self, temperature):
        '''
        Executes preprocessing logic

        temperature: temp for the ChatOpenAI model used in the react agent
        '''
        
        # Toggle On Activity Flag
        self.active = True

        try:
            # Depending on systems arguments, use either LM Studio's API or OpenAIs'
            is_lms = self.args.llm_platform == 'lm-studio'
            api_key = 'lm-studio' if is_lms else get_openai_api_key()
            model_name = self.args.lms_model if is_lms else self.args.openai_model

            model = ChatOpenAI(
                openai_api_key=api_key,
                model_name=model_name,
                temperature=temperature
            )
        except Exception as e:
            print(f'Error initializing ChatOpenAI model: {e}')


        #=======================================================#
        #  region   INITIALIZE PREPROCESSING AGENTS             #
        #=======================================================# 

        try:
            # AGENT1 = object to number and alias nulls handler
            agent1 = create_react_agent(model, tools)                                                                       
        except Exception as e:
            print(f'Error creating agent1 : A LanGraph prebuit ReAct agent: {e}')

        try:
            # AGENT2 = outlier and impute handler
            agent2 = create_react_agent(model, tools)                                                                       
        except Exception as e:
            print(f'Error creating agent2 : A LanGraph prebuit ReAct agent: {e}')

        #  endregion  ================================================#
        #  region  AGENT1 LOOP                                        #
        #=============================================================#       

        for column in preprocessor.get_df().columns:
            if column == self.args.target_var:
                continue

            # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = [] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            # OBJECT TO NUM AND ALIAS NULLS AGENT LOOP
            set_current_column(column)
            pipeline.write(f'set_current_column("{column}")')
            inputs = {'messages': [('user', AGENT1_IA["AGENT1_START"])]}
            try:
                stream = agent1.stream(inputs, stream_mode='values')
                print_stream(stream)
            except Exception as e:
                print(f'Error during stream: {e}')

        save_dataframe_stage(preprocessor.get_df(), 'POST_AGENT_1')

        #  endregion  ================================================#
        #  region  AGENT2 LOOP                                        #
        #=============================================================#       

        for column in preprocessor.get_df().columns:
            if column == self.args.target_var:
                continue

            # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = [] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            # Outlier and Impute Handler Loop
            set_current_column(column)
            pipeline.write(f'set_current_column("{column}")')
            inputs = {'messages': [('user', AGENT2_IA["AGENT2_START"])]}
            try:
                stream = agent2.stream(inputs, stream_mode='values')
                print_stream(stream)
            except Exception as e:
                print(f'Error during stream: {e}')

        save_dataframe_stage(preprocessor.get_df(), 'POST_AGENT_2')
        #  endregion

        # Toggle Off Activity Flag
        self.active = False

        return self.df # Return the most recent dataframe
    
    def update_df(self, altered_df):
        '''
        Updates the working dataframe so that the wordflow can continue.

        altered_df: altered version of the preprocessor dataframe
        '''
        self.backup_df = self.df.copy()
        self.df = altered_df.copy()

#  endregion  ================================================================================#
#  region                                FeatureEngineer                                      #
#=============================================================================================#

class FeatureEngineer:
    def __init__(self, args, df):
        self.args = args
        self.active = False
        
        self.original_df = df.copy()
        self.backup_df = df.copy()
        self.df = df.copy()

    def get_df(self):
        '''
        Return current df
        '''
        return self.df
    
    def set_df(self, df):
        '''
        Reassigns all dataframe variables
        '''
        self.original_df = df.copy()
        self.backup_df = df.copy()
        self.df = df.copy()

    def run(self, temperature):
        '''
        Executes feature engineering logic

        temperature: temp for the ChatOpenAI model used in the react agent
        '''

        # Toggle On Activity Flag
        self.active = True
        
        try:
            # Depending on systems arguments, use either LM Studio's API or OpenAIs'
            is_lms = self.args.llm_platform == 'lm-studio'
            api_key = 'lm-studio' if is_lms else get_openai_api_key()
            model_name = self.args.lms_model if is_lms else self.args.openai_model

            model = ChatOpenAI(
                openai_api_key=api_key,
                model_name=model_name,
                temperature=temperature
            )

            super_model = ChatOpenAI(
                openai_api_key=get_openai_api_key(),
                model_name=self.args.super_gpt_model,
                temperature=temperature
            )
        except Exception as e:
            print(f'Error initializing ChatOpenAI model: {e}')


        #=======================================================#
        #  region   INITIALIZE FEATURE ENGINEERING AGENTS       #
        #=======================================================# 

        try:
            # SUPER AGENT = Stronger GPT for Periodic Higher Inference Needs
            super_agent = create_react_agent(super_model, tools)
            set_super_agent(super_agent)
        except Exception as e:
            print(f'Error creating super_agent : A LanGraph prebuit ReAct agent: {e}')

        try:
            # AGENT3 = NLP Preliminary 
            agent3 = create_react_agent(model, [
                get_inst, logger, exec_stored_func,
                write_generated_func, exec_generated_func
            ])
        except Exception as e:
            print(f'Error creating agent3 : A LanGraph prebuit ReAct agent: {e}')
        
        try:
            # AGENT3_1 = NLP Row Iterator
            agent3_1 = create_react_agent(model, tools)
            set_agent3_1(agent3_1)
        except Exception as e:
            print(f'Error creating agent3_1 : A LanGraph prebuit ReAct agent: {e}')

        try:
            # AGENT4 = Column-wise / Categorical FE
            agent4 = create_react_agent(model, tools)                                                                       
        except Exception as e:
            print(f'Error creating agent4 : A LanGraph prebuit ReAct agent: {e}')

        try:
            # AGENT5 = DF-wise / Numeric FE
            agent5 = create_react_agent(model, tools)                                                                       
        except Exception as e:
            print(f'Error creating agent5 : A LanGraph prebuit ReAct agent: {e}')

        try:
            # AGENT6 = Final Feature Selector
            agent6 = create_react_agent(model, tools)                                                                       
        except Exception as e:
            print(f'Error creating agent6 : A LanGraph prebuit ReAct agent: {e}')

        #  endregion  ================================================#
        #  region  AGENT3 LOOP  Preliminary NLP                       #
        #=============================================================#      

        for column in feature_engineer.get_df().columns:
            if column == self.args.target_var:
                continue
            
            # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = ['col6'] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            set_current_column(column)
            pipeline.write(f'set_current_column("{column}")')
            inputs = {'messages': [('user', AGENT3_IA["AGENT3_START"])]}
            try:
                stream = agent3.stream(inputs, stream_mode='values')
                print_stream(stream)
            except Exception as e:
                print(f'Error during stream: {e}')          

        save_dataframe_stage(feature_engineer.get_df(), 'POST_AGENT_3')



        #  endregion  ================================================#
        #  region  AGENT4 LOOP                                        #
        #=============================================================#       

        for column in feature_engineer.get_df().columns:
            if column == self.args.target_var:
                continue
            
            # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = [] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            # OBJECT TO NUM AND ALIAS NULLS AGENT LOOP
            set_current_column(column)
            pipeline.write(f'set_current_column("{column}")')
            inputs = {'messages': [('user', AGENT4_IA["AGENT4_START"])]}
            try:
                stream = agent4.stream(inputs, stream_mode='values')
                print_stream(stream)
            except Exception as e:
                print(f'Error during stream: {e}')

        save_dataframe_stage(feature_engineer.get_df(), 'POST_AGENT_4')

        #  endregion  ================================================#
        #  region  AGENT5 LOOP                                        #
        #=============================================================#       

        for column in feature_engineer.get_df().columns:
            if column == self.args.target_var:
                continue
            
            # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = [] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            # OBJECT TO NUM AND ALIAS NULLS AGENT LOOP
            set_current_column(column)
            pipeline.write(f'set_current_column("{column}")')
            inputs = {'messages': [('user', AGENT5_IA["AGENT5_START"])]}
            try:
                stream = agent5.stream(inputs, stream_mode='values')
                print_stream(stream)
            except Exception as e:
                print(f'Error during stream: {e}')

        save_dataframe_stage(feature_engineer.get_df(), 'POST_AGENT_5')

        #  endregion  ================================================#
        #  region  AGENT6 LOOP                                        #
        #=============================================================#       

        for column in feature_engineer.get_df().columns:
            if column == self.args.target_var:
                continue
            
            # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = [] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            # OBJECT TO NUM AND ALIAS NULLS AGENT LOOP
            set_current_column(column)
            pipeline.write(f'set_current_column("{column}")')
            inputs = {'messages': [('user', AGENT6_IA["AGENT6_START"])]}
            try:
                stream = agent6.stream(inputs, stream_mode='values')
                print_stream(stream)
            except Exception as e:
                print(f'Error during stream: {e}')

        save_dataframe_stage(feature_engineer.get_df(), 'POST_AGENT_6')
        #  endregion

        # Toggle Off Activity Flag
        self.active = False
        
        # Return the most recent dataframe after all agent loops are completed
        return self.df
    
    def update_df(self, altered_df):
        '''
        Updates the working dataframe so that the wordflow can continue.

        altered_df: altered version of the feature_engineer dataframe
        '''
        self.backup_df = self.df.copy()
        self.df = altered_df.copy()

#  endregion  ================================================================================#
#  region                                File Management                                      #
#=============================================================================================#

def save_df_to_csv(args, df, csv_name=None):
    '''
    Saves dataframe to a .csv file

    df: dataframe
    csv_name: name (without extension) of output .csv
    '''
    csv_path = args.data_output_path

    # update path for custom name
    if csv_name:
        csv_path = os.path.join(os.path.dirname(args.data_output_path), f'{csv_name}.csv')

    # don't overwrite an existing .csv
    if os.path.exists(csv_path):
        print('Error: A dataframe is already saved under this name')
        return

    try:
        df.to_csv(csv_path, index=False)
        print(f'Dataframe saved to {csv_path}')
    except Exception as e:
        print(f'Error saving dataframe: {e}')

def init_pyfiles(args):
    '''
    Initialize global PyFile objects so that Tool Functions and classes have access from
    different scopes.

    args: system arguments
    '''
    global static_lib, pipeline_lib, sandbox, pipeline

    static_lib = PyFile(args.static_lib_path, args)
    pipeline_lib = PyFile(args.pipeline_lib_path, args)
    sandbox = PyFile(args.sandbox_path, args)
    pipeline = PyFile(args.pipeline_path, args)


def init_json_files():
    '''
    Verifys the json directory and creates the static_lib_json.json file

    args: system arguments
    '''
    if not os.path.exists(JSON_DIR):
        os.mkdir(JSON_DIR)

    with open(f'{JSON_DIR}/{STATIC_JSON_LIB}.json', "w") as json_file:
        json.dump(static_lib.get_func_objects(), json_file, indent=4)


def init_global_objects(args, df):
    '''
    Initialize global Preprocessor and FeatureEngineer objects
    
    args: system arguments
    df: pandas dataframe
    '''
    global preprocessor, feature_engineer, target_column

    preprocessor = Preprocesser(args, df)
    feature_engineer = FeatureEngineer(args, df)

    target_column = args.target_var


def save_pipeline_generation(args):
    '''
    Archives existing pipeline and dynamic_lib python files in the 

    args: system arguments
    '''
    if not os.path.exists(SAVED_GENS_DIR):
        os.makedirs(SAVED_GENS_DIR)

    # determine the generation ID by adding 1 to the highest detected saved generation
    try:
        folder_names = [name for name in os.listdir(SAVED_GENS_DIR) if os.path.isdir(os.path.join(SAVED_GENS_DIR, name))]
        generation_ids = []
        for name in folder_names:
            generation_ids.append(int(''.join([char for char in name if char.isdigit()])))
        generation_id = max(generation_ids) + 1 if generation_ids else 1
    except Exception as e:
        print(f'Error reading folder names of saved generations: {e}')
        raise Exception

    # create the save folder name
    save_dir_path = f'{SAVED_GENS_DIR}/GEN_{generation_id}'

    # ensure a duplicate save ID wasn't generated
    if os.path.exists(save_dir_path):
        print('A duplicate generation ID was received, try again')
        return
    
    # create the save directory
    os.mkdir(save_dir_path)

    # move and renames the pipeline, dynamic_lib, and data output files
    for path in [args.pipeline_path, args.pipeline_lib_path, args.sandbox_path, args.data_output_path]:
        if os.path.exists(path):
            base_name = os.path.basename(path)
            base_name_no_ext = os.path.splitext(base_name)[0]
            extension = 'csv' if 'csv' in base_name else 'py'
            shutil.move(path, f'{save_dir_path}/{base_name_no_ext}_{generation_id}.{extension}')

    print('Previous generation files have been archived')


def verify_lib_paths(args):
    '''
    Verify paths to library and pipeline files.

    args: system arguments
    '''
    try:

        # save any generated code before starting a new generation
        if os.path.exists(args.pipeline_path) or os.path.exists(args.pipeline_lib_path):
            pipeline_edited, pipeline_lib_edited = False, False
            try:
                pipeline_edited = open(args.pipeline_path, 'r').read() != PIPELINE_BOILERPLATE
            except Exception as e:
                pass
            try:
                pipeline_lib_edited = open(args.dynamic_lib_path, 'r').read() != PIPELINE_LIB_BOILERPLATE
            except Exception as e:
                pass

            # save the generation files if either lib is edited or an output file is found
            if pipeline_edited or pipeline_lib_edited or os.path.exists(args.data_output_path):
                save_pipeline_generation(args)

        # write boilerplate code to new files
        with open(args.pipeline_path, 'w') as file:
            file.write(PIPELINE_BOILERPLATE)
            file.close()
        with open(args.pipeline_lib_path, 'w') as file:
            file.write(PIPELINE_LIB_BOILERPLATE)
            file.close()
        with open(args.sandbox_path, 'w') as file:
            file.write('')
            file.close()

    except Exception as e:
        print(f'Error setting up pipeline and / or dynamic_lib path: {e}')

    # throw error if unable to locate static libs
    if not os.path.exists(args.static_lib_path):
        print('Error locating static_lib')
        return
    
    # verify data input path exists
    if not os.path.exists(args.data_input_path):
        print(f'Error: {args.data_input_path} does not exist')
        return


def run_ml_engineer(args):
    '''
    Verifys library files, loads dataset, sets global variables based on 
    system arguments, runs the preprocessor and feature_engineer, saves
    the resulting dataframe.
    
    args: system arguments
    '''
    try:
        verify_lib_paths(args)
    except Exception as e:
        print(f'Error verifying lib files: {e}')
        return
    
    # attempt to load dataset
    try:
        df = pd.read_csv(args.data_input_path, index_col=None)
    except Exception as e:
        print(f'Error reading csv to df: {e}')
        return
    
    # init PyFile objects once lib paths are verified
    init_pyfiles(args)

    # init json dir and files
    init_json_files()

    # load in the dataset
    pipeline.write(f'df = pd.read_csv("{args.data_input_path}", index_col=None)\n')

    # initialize the preprocessor and feature_engineer objects
    init_global_objects(args, df)

    # run the Preprocessor on the data
    preprocessed_df = preprocessor.run(temperature=0.5)
    
    # run the FeatureEngineer on the data
    feature_engineer.set_df(preprocessed_df)
    feature_engineered_df = feature_engineer.run(temperature=0.5)

    # save the final dataframe
    save_df_to_csv(args, feature_engineered_df)

#  endregion  ================================================================================#
#  region                                Entry Point w/ Argparser                             #
#=============================================================================================#

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_input_path', type=str, default='data_inputs/data.csv')
    parser.add_argument('--data_output_path', type=str, default='data_outputs/output.csv')
    parser.add_argument('--pipeline_path', type=str, default='runtime_lib/pipeline.py')
    parser.add_argument('--static_lib_path', type=str, default='runtime_lib/static_lib.py')
    parser.add_argument('--pipeline_lib_path', type=str, default='runtime_lib/pipeline_lib.py')
    parser.add_argument('--sandbox_path', type=str, default='runtime_lib/sandbox.py')

    parser.add_argument('--lms_model', type=str, default='LM Studio Community/Meta-Llama-3-8B-Instruct-GGUF')
    parser.add_argument('--openai_model', type=str, default='gpt-4o-mini')
    parser.add_argument('--super_gpt_model', type=str, default='gpt-4o')
    parser.add_argument('--llm_platform', type=str, default='openai')

    parser.add_argument('--target_var', type=str, default='target')
    parser.add_argument('--id_var', type=str)

    parser.add_argument('--debug', type=bool, default=False)

    args = parser.parse_args()
    run_ml_engineer(args)

# Jesse Terminal Run
# /opt/anaconda3/envs/Agentic-ML-Engineer/bin/python main.py --llm_platform=openai --debug=True


#  endregion