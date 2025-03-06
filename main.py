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
from runtime_lib.static_agent_libs.agent2_1_static_lib import *
from runtime_lib.static_agent_libs.agent3_static_lib import *
from runtime_lib.static_agent_libs.agent4_static_lib import *
from runtime_lib.static_agent_libs.agent5_static_lib import *
from runtime_lib.static_agent_libs.agent6_static_lib import *

import runtime_lib.static_agent_libs.agent1_static_lib as agent1
import runtime_lib.static_agent_libs.agent2_static_lib as agent2
import runtime_lib.static_agent_libs.agent2_1_static_lib as agent2_1
import runtime_lib.static_agent_libs.agent3_static_lib as agent3
import runtime_lib.static_agent_libs.agent4_static_lib as agent4
import runtime_lib.static_agent_libs.agent5_static_lib as agent5
import runtime_lib.static_agent_libs.agent6_static_lib as agent6

# List of agent modules
AGENT_MODULES = [agent1, agent2, agent2_1, agent3, agent4, agent5, agent6]

# INSTRUCTION ARCHIVE LIST: Used in the get_inst tool
IA_LIST = [INST_ARCHIVE, AGENT1_IA, AGENT2_IA, AGENT2_1_IA, AGENT3_IA, AGENT4_IA, AGENT5_IA, AGENT6_IA]

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
    # Special handling for dataset goal instructions
    if inst_key == "DATA_SET_GOAL":
        dataset_goal = get_shared_var('dataset_goal')
        if dataset_goal:
            return f"DATASET GOAL: {dataset_goal}\n"
        return "DATASET GOAL: No specific goal provided for this dataset.\n"

    # Regular instruction lookup
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

    print(f"{get_shared_var('current_agent_name')} is attempting to run {func_name} on the '{get_shared_var('current_column')}' column")

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

    print(f"{get_shared_var('current_agent_name')} is attempting to run {func_name} on the '{get_shared_var('current_column')}' column")

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
def append_to_json_list(
    new_items: Annotated[list, "The list of items to be added to the JSON list."],
    json_path: Annotated[str, "The file path to the JSON file to which items will be appended."]
) -> str:
    """
    Appends new items to the existing list in the JSON file specified by json_path.
    If the file doesn't exist or is empty, it initializes the file with an empty list.

    Example JSON structure:
    ["item1", "item2", "item3"]
    
    Parameters:
        new_items (list): The list of strings to append.
        json_path (str): The file path to the JSON file.

    Returns:
        str: A success message or error message.
    """
    try:
        # Ensure the input is a list of strings.
        if not isinstance(new_items, list):
            return "Error: The provided data is not a list."
        if not all(isinstance(item, str) for item in new_items):
            return "Error: All items in the list must be strings."

        # If the file doesn't exist or is empty, initialize it with an empty list.
        if not os.path.exists(json_path) or os.path.getsize(json_path) == 0:
            with open(json_path, "w") as file:
                json.dump([], file, indent=4)
            print(f"Initialized empty JSON file at {json_path}.")

        # Load the existing list from the JSON file.
        with open(json_path, "r") as file:
            current_list = json.load(file)

        # Append the new items to the list and remove duplicates.
        current_list.extend(new_items)
        current_list = list(set(current_list))

        # Save the updated list back to the JSON file.
        with open(json_path, "w") as file:
            json.dump(current_list, file, indent=4)

        return f"Items successfully added: {new_items}"

    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool
def add_nlp_column(
    column: Annotated[str, 'the name of the NLP column being added.']
) -> str:
    '''
    Appends a new NLP column to the global list of NLP columns.
    '''
    current_nlp_columns = get_shared_var('nlp_columns')
    if column not in current_nlp_columns:
        current_nlp_columns.append(column)
        set_shared_var('nlp_columns', current_nlp_columns)
        return(f'Successfully add column to NLP columns: {column}')
    return(f'Column already in NLP columns: {column}')

@tool
def get_pow_candidates(
    column_type: Annotated[str, 'either "numeric" or "object"'] = 'numeric'
) -> str:
    '''
    Returns a list of columns to be examined as potential parts-of-a-whole column groups.
    '''
    df = preprocessor.get_df() if preprocessor.active else feature_engineer.get_df()
    candidates_string = 'The following first entry is the column you are to build a parts-of-a-whole group around:'
    if column_type == 'numeric':
        pow_cols = [get_shared_var('compare_col')] + get_shared_var('ungrouped_cols')
        for c in pow_cols:
            col_data = df[c].dropna()  # Remove NaN values for accurate statistics
            min_val = col_data.min()
            q1 = col_data.quantile(0.25)
            q2 = col_data.median()
            q3 = col_data.quantile(0.75)
            max_val = col_data.max()
            candidates_string += (
                f"\n- {'COMPARE COLUMN: ' if c == get_shared_var('compare_col') else ''}{c} (dtype: {df[c].dtype}): "
                f"Min={min_val}, Q1={q1}, Median={q2}, Q3={q3}, Max={max_val}"
            )

    if column_type == 'object':
        pow_cols = [c for c in df.columns if c not in get_shared_var('skip_columns') and pd.api.types.is_object_dtype(df[c])]
        for c in pow_cols:
            col_data = df[c].dropna()  # Remove NaN values for accurate statistics
            unique_vals = col_data.nunique()
            candidates_string += (
                f"\n- {c} (dtype: {df[c].dtype}): {unique_vals} unique values"
            )

    return f'Parts-of-a-whole {column_type} column candidates include the following:\n{candidates_string}'

@tool
def create_pow_group(
    group: Annotated[list, 'a list of column names that you\'ve determined are logically related or parts-of-a-whole'],
    column_type: Annotated[str, 'either "numeric" or "object"'] = 'numeric'
) -> str:
    '''
    Stores a parts-of-a-whole column group.
    '''
    try:
        ungrouped_cols = get_shared_var('ungrouped_cols')

        # Columns may belong to only one group
        set_shared_var('ungrouped_cols', [c for c in ungrouped_cols if c not in group])

        if column_type == 'numeric':
            numeric_pow_groups = get_shared_var('numeric_pow_groups')
            numeric_pow_groups.append(group)
            set_shared_var('numeric_pow_groups', numeric_pow_groups)
        elif column_type == 'object':
            object_pow_groups = get_shared_var('object_pow_groups')
            object_pow_groups.append(group)
            set_shared_var('object_pow_groups', object_pow_groups)
        else:
            return f'Column type is invalid: {column_type}'
    except Exception as e:
        return f'Error setting parts-of-a-whole column groupings shared variable: {e}'
    return f'Successfully stored parts-of-a-whole groupings.'

@tool
def describe_pow_group() -> str:
    '''
    Returns relevant column descriptions of the columns in the current parts-of-a-whole column group.
    '''
    try:
        numeric_transform_columns = get_shared_var('numeric_transform_columns')
        numeric_transform_names = numeric_transform_columns if isinstance(numeric_transform_columns, list) else []
        already_created_columns = f'The following columns have already been created: {numeric_transform_names}. Do not create them again.'

        pow_group = get_shared_var('current_pow_group')
        if not pow_group:
            return 'No parts-of-a-whole column group is currently selected.'
        
        df = preprocessor.get_df() if preprocessor.active else feature_engineer.get_df()
        descriptions = []
        
        for col in pow_group:
            if pd.api.types.is_numeric_dtype(df[col]):
                descriptions.append(
                    f'"{col}"\n (dtype: {df[col].dtype}): '
                    f'min={df[col].min():.2f}, '
                    f'mean={df[col].mean():.2f}, '
                    f'max={df[col].max():.2f}'
                )
            else:
                descriptions.append(
                    f'"{col}"\n (dtype: {df[col].dtype}): '
                    f'{df[col].nunique()} unique values'
                )
                
        return already_created_columns + '\n\n' + '\n'.join(descriptions)

    except Exception as e:
        return f"Error: {str(e)}"

@tool
def test_pow_transform(
    column_creation_code: Annotated[str, '''A string of code that will create the new column feature. 
                                          MUST include new column name assignment.
                                          Example: df["new_feature"] = df["col1"] * df["col2"]''']
) -> str:
    '''
    Tests executing the provided code string that creates a new transformed column from parts-of-a-whole columns.
    Returns a success or error message.
    '''
    try:
        # Verify the code includes a column assignment
        if '=' not in column_creation_code:
            return "Error: Column creation code must include an assignment (=) to create a new column. Example: df['new_feature'] = calculation"
        
        # Split the code to get the new column name - handle both single and double quotes
        left_side = column_creation_code.split('=')[0].strip()
        if "df['" in left_side:
            new_col_name = left_side.split("df['")[1].split("']")[0]
        elif 'df["' in left_side:
            new_col_name = left_side.split('df["')[1].split('"]')[0]
        else:
            return "Error: Invalid column assignment format. Must use df['column_name'] or df['column_name']"
        
        df = preprocessor.get_df() if preprocessor.active else feature_engineer.get_df()
        
        # Create local scope with copy of dataframe and pandas import
        local_vars = {'df': df.copy(), 'pd': pd}
        
        # Execute the transformation
        exec(column_creation_code, globals(), local_vars)
        
        # Get the updated dataframe from local scope
        updated_df = local_vars['df']
        
        # Verify the new column exists and update the working dataframe
        if new_col_name in updated_df.columns:
            
            # Check if column already exists in working dataframe
            working_df = preprocessor.get_df() if preprocessor.active else feature_engineer.get_df()
            if new_col_name in working_df.columns:
                return f"Error: Column '{new_col_name}' already exists in the working dataframe. Choose a different name."
            
            if preprocessor.active:
                preprocessor.update_df(updated_df)
            else:
                feature_engineer.update_df(updated_df)
            
            # Archive the new column name
            numeric_transform_columns = get_shared_var('numeric_transform_columns')
            if new_col_name not in numeric_transform_columns:
                numeric_transform_columns.append(new_col_name)
                set_shared_var('numeric_transform_columns', numeric_transform_columns)
            
            return f"Column creation code executed successfully. The new column has been archived: {new_col_name}"
        else:
            return f"Error: The new column '{new_col_name}' was not created successfully."

    except Exception as e:
        return f"Error executing transformation code: {str(e)}"

@tool
def encode_choice(encoding_category: str, extra_info: dict = None):
    """
    Adds the current column (retrieved via get_shared_var('current_column')) to the encode_selections 
    dictionary under the specified encoding_category.
    
    Parameters:
      encoding_category (str): One of the following keys:
        'Numeric_Encode'
        'One_Hot_Encode'
        'Frequency_Count_Encode'
        'Ordinal_Encode'
        'NLP_Handler'
        'Scale_Or_Normalize'
        'Failed_Encode_Selection'
          
    Returns:
      str: A confirmation message indicating the column was added.
    """
    # Retrieve the current column from the shared variable
    column = get_shared_var('current_column')
    if column is None:
        raise ValueError("The shared variable 'current_column' is not set.")
    
    encode_selections = get_shared_var('encode_selections')
    
    # Validate the encoding category exists in the dictionary
    if encoding_category not in encode_selections:
        raise ValueError(f"Encoding category '{encoding_category}' is not recognized.")
    
    # For 'Bin_Numeric', expect extra_info to include the number of bins
    if encoding_category == 'Bin_Numeric':
        if extra_info is None or 'n_bins' not in extra_info:
            raise ValueError("For 'Bin_Numeric', extra_info with key 'n_bins' must be provided.")
        # Append as a tuple (column, n_bins)
        encode_selections[encoding_category].append((column, extra_info['n_bins']))
    else:
        # For other categories, add the column if it isn't already present
        if column not in encode_selections[encoding_category]:
            encode_selections[encoding_category].append(column)
    
    set_shared_var('encode_selections', encode_selections)
    
    return f"Added column '{column}' to '{encoding_category}'"

@tool
def redundancy_dictionary(key_item: str, value_items: list, extra_info: dict = None):
    """
    Updates the redundancy dictionary with a canonical key and its associated redundant variations,
    organized by the current column.

    This tool retrieves the shared variable 'redundancy_dictionary'. If it doesn't exist,
    it creates one. It then gets the current column name via get_shared_var('current_column') and 
    ensures there is a dedicated dictionary for that column. Finally, it either creates a new entry 
    for the provided key_item or appends any new value items to the existing list (avoiding duplicates).

    Parameters:
      key_item (str): The canonical value (e.g., "1-99") considered the primary label.
      value_items (list): A list of redundant variations (e.g., ["[1-99]", "(1-99)"]).
      extra_info (dict): Optional extra information (not used in this implementation).

    Returns:
      str: A confirmation message indicating the update to the redundancy dictionary for the current column.
    """
    # Retrieve the current column name
    column = get_shared_var('current_column')

    # Retrieve the full redundancy dictionary; if not present, initialize it.
    redundancy_dict = get_shared_var('redundancy_dictionary')
    if redundancy_dict is None:
        redundancy_dict = {}

    # Ensure there is a dictionary for the current column
    if column not in redundancy_dict:
        redundancy_dict[column] = {}

    # Work on the dictionary for the current column
    column_dict = redundancy_dict[column]

    # If the key already exists, add new values (avoiding duplicates)
    if key_item in column_dict:
        for item in value_items:
            if item not in column_dict[key_item]:
                column_dict[key_item].append(item)
    else:
        column_dict[key_item] = value_items

    # Update the main redundancy dictionary with the modified column data
    redundancy_dict[column] = column_dict
    set_shared_var('redundancy_dictionary', redundancy_dict)
    
    return f"Updated redundancy dictionary for column '{column}': key '{key_item}' now maps to {column_dict[key_item]}"


@tool
def request_human_approval(task_to_approve):
    """
    Requests human approval before executing the next function.
    Returns 'approved' if approved, otherwise 'denied'.
    """
    user_input = input(f"Do you approve running {task_to_approve}? (yes/no): ").strip().lower()
    return "approved" if user_input == "yes" else "denied"


tools = [
    get_inst,
    logger,
    exec_stored_func,
    append_to_json_list,
    add_nlp_column,
    encode_choice,
    redundancy_dictionary,
    request_human_approval
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
        
        try:
            # AGENT2_1 = Redundancy Dictionary Executer
            agent2_1 = create_react_agent(model, tools)                                                                       
        except Exception as e:
            print(f'Error creating agent2_1 : A LanGraph prebuit ReAct agent: {e}')

        #  endregion  ================================================#
        #  region  AGENT1 LOOP                                        #
        #=============================================================#       
        set_shared_var('current_agent_name', 'Agent 1')

        for column in preprocessor.get_df().columns:
            if column == self.args.target_var:
                continue

            # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = ['home.dest'] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            # OBJECT TO NUM AND ALIAS NULLS AGENT LOOP
            set_shared_var('current_column', column)
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
        set_shared_var('current_agent_name', 'Agent 2')       

        for column in preprocessor.get_df().columns:
            if column == self.args.target_var:
                continue

            # # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = ['home.dest'] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            # Outlier and Impute Handler Loop
            set_shared_var('current_column', column)
            set_shared_var('target_column', args.target_var)
            pipeline.write(f'set_current_column("{column}")')
            inputs = {'messages': [('user', AGENT2_IA["AGENT2_START"])]}
            try:
                stream = agent2.stream(inputs, {"recursion_limit": 100}, stream_mode='values')
                print_stream(stream)
            except Exception as e:
                print(f'Error during stream: {e}')
        
        # UPDATE!! This is overwritten too easily Save Redundancy Dictionary to Json 
        # with open('json_lib/saved_redundancy_dictionary.json', 'w') as file:
        #     json.dump(get_shared_var('redundancy_dictionary'), file, indent=4)
        #     print('Saved Redundancy Dictionary To Json')

        save_dataframe_stage(preprocessor.get_df(), 'POST_AGENT_2')

        #  endregion  ================================================#
        #  region  AGENT2_1 LOOP                                        #
        #=============================================================#
        set_shared_var('current_agent_name', 'Agent 2_1')       

        for column in preprocessor.get_df().columns:
            if column == self.args.target_var:
                continue

            # # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = ['home.dest'] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            # Outlier and Impute Handler Loop
            set_shared_var('current_column', column)
            set_shared_var('target_column', args.target_var)
            pipeline.write(f'set_current_column("{column}")')
            inputs = {'messages': [('user', AGENT2_1_IA["AGENT2_1_START"])]}
            try:
                stream = agent2_1.stream(inputs, {"recursion_limit": 100}, stream_mode='values')
                print_stream(stream)
            except Exception as e:
                print(f'Error during stream: {e}')
        
        save_dataframe_stage(preprocessor.get_df(), 'POST_AGENT_2_1')

#  endregion  ================================================================================#
#  region                               Close Out Preprocessor                                #
#=============================================================================================#

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
            super_agent = create_react_agent(super_model, [
                get_inst, logger, exec_stored_func, get_pow_candidates, create_pow_group
            ])
            set_shared_var('super_agent', super_agent)
        except Exception as e:
            print(f'Error creating super_agent : A LanGraph prebuit ReAct agent: {e}')

        try:
            # AGENT3 = NLP Preliminary 
            agent3 = create_react_agent(super_model, [
                get_inst, logger, exec_stored_func, append_to_json_list,
                write_generated_func, exec_generated_func
            ])
        except Exception as e:
            print(f'Error creating agent3 : A LanGraph prebuit ReAct agent: {e}')
        
        try:
            # AGENT3_1 = NLP Row Iterator
            agent3_1 = create_react_agent(model, tools)
            set_shared_var('agent3_1', agent3_1)
        except Exception as e:
            print(f'Error creating agent3_1 : A LanGraph prebuit ReAct agent: {e}')

        try:
            # AGENT4 = Column-wise / Categorical FE
            agent4 = create_react_agent(model, tools)                                                                       
        except Exception as e:
            print(f'Error creating agent4 : A LanGraph prebuit ReAct agent: {e}')

        try:
            # AGENT5 = DF-wise / Numeric FE
            agent5 = create_react_agent(model, [
                get_inst, logger, describe_pow_group, test_pow_transform
            ])
        except Exception as e:
            print(f'Error creating agent5 : A LanGraph prebuit ReAct agent: {e}')

        try:
            # AGENT6 = Final Feature Selector
            agent6 = create_react_agent(super_model, [
                get_inst, exec_stored_func, encode_choice
            ])                                                                       
        except Exception as e:
            print(f'Error creating agent6 : A LanGraph prebuit ReAct agent: {e}')


        #  endregion  ================================================#
        #  region  AGENT3 LOOP  Preliminary NLP                       #
        #=============================================================#      
        set_shared_var('current_agent_name', 'Agent 3')

        for column in feature_engineer.get_df().columns:
            if column == self.args.target_var:
                continue
            
            # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = [] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            set_shared_var('current_column', column)
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
        set_shared_var('current_agent_name', 'Agent 4')

        for column in feature_engineer.get_df().columns:
            if column == self.args.target_var:
                continue
            
            # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                COLUMNS_TO_TEST = [] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            # OBJECT TO NUM AND ALIAS NULLS AGENT LOOP
            set_shared_var('current_column', column)
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
        set_shared_var('current_agent_name', 'Agent 5 Super')

        # DEBUG use do_pow_search flag to toggle POW agents
        if feature_engineer.args.do_pow_search:

            # Initialize parts-of-a-whole search
            search_exhausted = False
            iteration_count = 0
            max_iterations = 100  # Safety limit to prevent infinite loops
            
            # Setup initial columns
            set_shared_var('skip_columns', [self.args.target_var, self.args.id_var])
            ungrouped_cols = [c for c in self.get_df().columns 
                            if c not in get_shared_var('skip_columns') 
                            and pd.api.types.is_numeric_dtype(self.get_df()[c])]
            set_shared_var('ungrouped_cols', ungrouped_cols)
            
            while not search_exhausted:
                iteration_count += 1
                ungrouped_cols = get_shared_var('ungrouped_cols')
                
                # Multiple conditions to exit the loop
                if (len(ungrouped_cols) <= 1  # Skip last column if it's a straggler
                    or iteration_count >= max_iterations  # Safety limit reached
                    or not ungrouped_cols):  # No more columns to process
                    search_exhausted = True
                    print(f"Search completed after {iteration_count} iterations")
                    break
                
                # Process next column
                compare_col = ungrouped_cols.pop(0)
                set_shared_var('compare_col', compare_col)
                set_shared_var('ungrouped_cols', ungrouped_cols)
                
                print(f"Processing column {compare_col}. Remaining columns: {len(ungrouped_cols)}")
                
                inputs = {'messages': [('user', AGENT5_IA["SUPER_AGENT5_START"])]}
                try:
                    stream = super_agent.stream(inputs, stream_mode='values')
                    print_stream(stream)
                except Exception as e:
                    print(f'Error during stream: {e}')
                    # Don't let errors break the loop
                    continue

            set_shared_var('current_agent_name', 'Agent 5')

            # Process the groups as before
            for group in get_shared_var('numeric_pow_groups'):
                set_shared_var('current_pow_group', group)
                for i in range(self.args.pow_iter):
                    inputs = {'messages': [('user', AGENT5_IA["AGENT5_START"])]}
                    try:
                        stream = agent5.stream(inputs, stream_mode='values')
                        print_stream(stream)
                    except Exception as e:
                        print(f'Error during stream: {e}')

            print(f'\n\nSearch Alg Approach Pow Groups: {get_shared_var("numeric_pow_groups")}\n')
            print(f'ITER=5 Recursive Feature Creation: {get_shared_var("numeric_transform_columns")}\n\n')

        save_dataframe_stage(self.get_df(), 'POST_AGENT_5')

        #  endregion  ================================================#
        #  region  AGENT6 LOOP (ENCODE AGENT)                         #
        #=============================================================#    
        set_shared_var('current_agent_name', 'Agent 6')

        for column in feature_engineer.get_df().columns:
            if column == self.args.target_var:
                continue
            
            # DEBUGGING: Run iteration of small column set or a single column
            if self.args.debug:
                # For quick paste: 'col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8'
                COLUMNS_TO_TEST = ['title', 'description'] # Empty to Skip Agent Entirely!
                if column not in COLUMNS_TO_TEST:
                    continue
            
            # ENCODE SELECTION AGENT
            set_shared_var('current_column', column)
            pipeline.write(f'set_current_column("{column}")')
            inputs = {'messages': [('user', AGENT6_IA["AGENT6_START"])]}
            try:
                stream = agent6.stream(inputs, stream_mode='values')
                print_stream(stream)
            except Exception as e:
                print(f'Error during stream: {e}')

        with open('json_lib/saved_encode_selections.json', 'w') as file:
            json.dump(get_shared_var('encode_selections'), file, indent=4)


        # Consolidate NLP columns if there are multiple
        encode_selections = get_shared_var('encode_selections')
        nlp_columns = encode_selections.get('NLP_Handler', [])
        
        if len(nlp_columns) > 1:
            print(f"Found multiple NLP columns: {nlp_columns}. Consolidating...")
            
            # Create cumulative column name
            cumulative_col_name = "cumulative_nlp_text"
            
            # Combine text from all NLP columns with space separator
            df = feature_engineer.get_df()
            df[cumulative_col_name] = df[nlp_columns].astype(str).agg(' '.join, axis=1)
            
            # Remove original NLP columns
            df = df.drop(columns=nlp_columns)

            feature_engineer.update_df(df)
            
            # Update encode_selections with new cumulative column
            encode_selections['NLP_Handler'] = [cumulative_col_name]
            set_shared_var('encode_selections', encode_selections)
            
            # Update the JSON file
            with open('json_lib/saved_encode_selections.json', 'w') as file:
                json.dump(encode_selections, file, indent=4)
            
            print(f"Created consolidated NLP column: {cumulative_col_name}")
            print(f"Removed original columns: {nlp_columns}")


        #  ===========================================================#
        #  region START: AGENT6 Encode Execution                      #
        #=============================================================# 

        with open('json_lib/saved_encode_selections.json', "r") as file:
            encode_selections = json.load(file)

        # Dictionary mapping encode_selections keys to their corresponding function calls
        encoding_functions = {
            # "Numeric_Encode": execute_numeric_encode,  # Tree Models Only
            # "One_Hot_Encode": execute_one_hot_encode,  # Neural Network Models Only
            # "Frequency_Count_Encode": execute_frequency_encode,  # Future Feature (Not Currently Active)
            # "Ordinal_Encode": execute_ordinal_encode, # Future Feature (Not Currently Active)
            "NLP_Handler": execute_nlp_handler,
            # "Scale_Or_Normalize": execute_scaling_normalization,

        }

        df6 = feature_engineer.get_df()  # Load the DataFrame once

        # Iterate over each encoding category in encode_selections
        for encode_type, columns in encode_selections.items():
            # Check if there is a function mapped for this encoding type
            if encode_type in encoding_functions:
                encoding_function = encoding_functions[encode_type]  # Get corresponding function

                # Apply the encoding function to each column
                for column in columns:
                    if column in df6.columns:  # Ensure the column exists in the DataFrame
                        df6 = encoding_function(df6, column)  # Apply encoding
                    else:
                        print(f"Warning: Column '{column}' not found in DataFrame. Skipping...")
        
        # Save the Final Encode Reference Dictionary
        with open('json_lib/saved_encode_dictionary.json', 'w') as file:
            json.dump(get_shared_var('column_mappings'), file, indent=4)

        print("Encode Dictionary updated and JSON file written.")

        #  ===========================================================#
        #  region END: AGENT6 Encode Execution                      #
        #=============================================================#

        # save dataframe with newly encoded columns
        feature_engineer.update_df(df6)
        save_dataframe_stage(df6, 'POST_AGENT_6')

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


def init_json_files(args):
    '''
    Verifies the json directory and creates/reads necessary json files static_lib_json.json and dataset_goals.json
    
    args: system arguments
    '''
    if not os.path.exists(JSON_DIR):
        os.mkdir(JSON_DIR)

    # Create static lib json
    with open(f'{JSON_DIR}/{STATIC_JSON_LIB}.json', "w") as json_file:
        json.dump(static_lib.get_func_objects(), json_file, indent=4)

    # Read dataset goals json is dataset goal is specified
    goal_id = args.dataset_goal_id
    if goal_id != 'default':
        dataset_goals_path = f'{JSON_DIR}/dataset_goals.json'
        try:
            if os.path.exists(dataset_goals_path):
                with open(dataset_goals_path, 'r') as file:
                    dataset_goals_dict = json.load(file)
                    
                    if goal_id in dataset_goals_dict.keys():
                        set_shared_var('dataset_goal', dataset_goals_dict[goal_id])
                    else:
                        print(f'Warning: Goal ID "{goal_id}" not found in dataset_goals.json. Available goals: {list(dataset_goals_dict.keys())}')
            else:
                print(f'Warning: {dataset_goals_path} not found. Dataset goals will not be loaded.')
        except Exception as e:
            print(f'Error reading dataset goals json: {e}')


def init_global_objects(args, df):
    '''
    Initialize global Preprocessor and FeatureEngineer objects
    
    args: system arguments
    df: pandas dataframe
    '''
    global preprocessor, feature_engineer

    preprocessor = Preprocesser(args, df)
    feature_engineer = FeatureEngineer(args, df)

    set_shared_var('target_column', args.target_var)
    set_shared_var('max_nlp_token_features', args.max_nlp_token_features)


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
    init_json_files(args)

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
    parser.add_argument('--data_input_path', type=str, default='data_inputs/data-arti-300/titanic_passenger_list.csv')
    parser.add_argument('--data_output_path', type=str, default='data_outputs/output.csv')
    parser.add_argument('--pipeline_path', type=str, default='runtime_lib/pipeline.py')
    parser.add_argument('--static_lib_path', type=str, default='runtime_lib/static_lib.py')
    parser.add_argument('--pipeline_lib_path', type=str, default='runtime_lib/pipeline_lib.py')
    parser.add_argument('--sandbox_path', type=str, default='runtime_lib/sandbox.py')

    parser.add_argument('--lms_model', type=str, default='LM Studio Community/Meta-Llama-3-8B-Instruct-GGUF')
    parser.add_argument('--openai_model', type=str, default='gpt-4o') #gpt-4o-mini
    parser.add_argument('--super_gpt_model', type=str, default='gpt-4o')
    parser.add_argument('--llm_platform', type=str, default='openai')
    
    parser.add_argument('--do_pow_search', type=bool, default=False)
    parser.add_argument('--pow_iter', type=int, default=2)
    parser.add_argument('--max_nlp_token_features', type=int, default=1000)
    
    parser.add_argument('--target_var', type=str, default='survived')
    parser.add_argument('--id_var', type=str)

    # parser.add_argument('--dataset_goal_id', type=str, default='default')
    parser.add_argument('--dataset_goal_id', type=str, default='fake_job_postings')

    parser.add_argument('--debug', type=bool, default=False)

    args = parser.parse_args()
    run_ml_engineer(args)

# Terminal Run & Flag Examples
# /opt/anaconda3/envs/Agentic-ML-Engineer/bin/python main.py --llm_platform=openai --debug=True

# Alternate dataset with ID column pre-specification
# python .\main.py --debug=True --do_pow_search=True --data_input_path=data_inputs/pow_testing.csv --id_var=ID

# python .\main.py --debug=True --dataset_goal_id=fake_job_postings

#  endregion