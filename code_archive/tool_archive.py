# @tool
# def search_lib() -> str:
#     '''
#     Returns the static function library as a JSON string of all available functions.
#     example function: {'function_name': [val], 'description': [val]}
#     '''
#     with open(f'{JSON_DIR}/{STATIC_JSON_LIB}.json', "r") as json_file:
#         return json_file.read()
    


# @tool
# def iteration_wrapper():
#     '''
#     Used to execute a column-wise function on multiple columns.
#     '''
#     pass



# @tool
# def write_to_pipeline(
#     code: Annotated[str, 'string of the code being appended onto the existing pipeline']
# ) -> str:
#     '''
#     Writes the given code to the pipeline.py file
#     '''
#     try:
#         pipeline.write(code)
#         return 'Successfully wrote code to pipeline'
#     except Exception as e:
#         return f'Error writing to pipeline: {e}'



# # Define the path to your task list JSON file
# TASK_LIST_PATH = "json_lib/task_list.json"

# @tool
# def add_task_to_list(new_task: str) -> str:
#     '''
#     Appends a new task to json_lib/task_list.json.

#     Args:
#         new_task (str): The task to be added to the task list.

#     Returns:
#         str: A confirmation message indicating the task was added successfully.

#     Example JSON structure:
#     [
#         {
#             "task": "Remove any duplicates from the df."
#         },
#         {
#             "task": "Handle the null values in the df."
#         }
#     ]
#     '''
#     try:
#         # Load the existing task list from the JSON file
#         with open(TASK_LIST_PATH, "r") as file:
#             task_list = json.load(file)

#         # Append the new task
#         task_list.append({"task": new_task})

#         # Save the updated task list back to the JSON file
#         with open(TASK_LIST_PATH, "w") as file:
#             json.dump(task_list, file, indent=4)

#         return f"Task successfully added: {new_task}"

#     except FileNotFoundError:
#         return "Error: Task list file not found."

#     except json.JSONDecodeError:
#         return "Error: Task list file is not in a valid JSON format."

#     except Exception as e:
#         return f"An unexpected error occurred: {e}"



# @tool
# def write_generated_func(
#     code: Annotated[str, 'string of the code being fused into dynamic_lib.py for further access']
# ) -> str:
#     '''
#     Writes the given code to the sandbox.
#     '''
#     sandbox.reset() # clear any leftover output

#     try:
#         sandbox.write(code + '\n')
#         return 'Successfully added function to the sandbox'
#     except Exception as e:
#         return f'Error writing generated function: {e}'



# @tool
# def exec_generated_func(
#     func_name: Annotated[str, 'name of the generated function to be run'],
#     func_call_code: Annotated[str, '''The code (usually one line) to call the function. Include all necessary parameter values except for df and column,
#                               those will be assigned locally--leave them explicity as 'df' and 'column'. Always include "output = " before the call to catch return values. Format examples:
#                               output = func_name(df, column, param1=value1), output = func_name(df, column), output = func_name(df)''']
# ) -> str:
#     """
#     Executes a dynamically generated function on the current working dataframe
#     and writes the function call to the pipeline file.
#     """
#     print(f"Agent is attempting to run {func_name} on the '{current_column}' column")

#     try:
#         # Get the function code from the sandbox
#         func_code = sandbox.read()

#         # Dynamically define the function in the local context
#         exec(func_code, globals())
#         func = globals().get(func_name)

#         if func is None:
#             raise ValueError(f'Function {func_name} could not be defined.')
#     except Exception as e:
#         return f'Error loading function from sandbox: {e}'

#     try:
#         # Dynamically execute the function call code
#         local_vars = {'df': preprocessor.get_df(), 'column': current_column, 'target': TARGET_VAR_NAME}
#         exec(func_call_code, globals(), local_vars)

#         # Capture the updated DataFrame (if any)
#         output = local_vars.get('output', None)

#         # Update the preprocessor's DataFrame if the function modifies it in place or returns it
#         updated_df = output if isinstance(output, pd.DataFrame) else local_vars.get('df', None)
#         if isinstance(updated_df, pd.DataFrame):
#             preprocessor.update_df(updated_df)
#         else:
#             print('Error updating local dataframe')
#     except Exception as e:
#         return f'Error executing function locally: {e}'

#     try:
#         # Write the function call code to the pipeline file
#         if func_call_code[:8] == 'output =':
#             func_call_code = 'df =' + func_call_code[8:]
        
#         # Regex to identify 'column' and 'target' as arguments without explicit values
#         column_pattern = r'\bcolumn\b(?=(\s*,|\s*\)|$))'
#         target_pattern = r'\btarget\b(?=(\s*,|\s*\)|$))'

#         # Replace 'column' with the current_column when it's used as a parameter without an explicit value
#         func_call_code = re.sub(column_pattern, f'"{str(current_column)}"', func_call_code)

#         # Replace 'target' with TARGET_VAR_NAME when it's used as a parameter without an explicit value
#         func_call_code = re.sub(target_pattern, f'"{str(TARGET_VAR_NAME)}"', func_call_code)
        
#         pipeline.write(func_call_code)

#         # Save the function code from the sandbox to the pipeline_lib
#         pipeline_lib.write(func_code)
#         sandbox.reset()

#         return f'Successfully executed and saved function: {func_name}'
#     except Exception as e:
#         return f'Error writing function call to pipeline: {e}'