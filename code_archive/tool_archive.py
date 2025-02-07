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