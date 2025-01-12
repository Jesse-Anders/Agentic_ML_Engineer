import os
import json
import importlib.util
from typing import Annotated

import pandas as pd
from dotenv import load_dotenv

# LangGraph & associated imports
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import toolbox
import inspect


# ---------------------------------------------------------------------------
# 0) LOAD ENV VARS FOR OPENAI KEY
# ---------------------------------------------------------------------------
load_dotenv()

def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY")

# ---------------------------------------------------------------------------
# 0) LOAD DATA INTO DATAFRAME DF
# ---------------------------------------------------------------------------
# Register a DataFrame
data_file_name = "data.csv"
df = pd.read_csv(data_file_name)

# ---------------------------------------------------------------------------
# 1) DEFINE TOOLS: "WRITE_CODE_TO_FILE" AND "EXECUTE_GENERATED_CODE"
# ---------------------------------------------------------------------------
@tool
def write_code_to_file(
    filename: Annotated[str, "Name of the file to write (e.g. 'new_tool.py')"],
    code: Annotated[str, "The code to write into the file"]
) -> str:
    """
    Writes the provided 'code' to a file named 'filename'.
    Overwrites if the file exists.
    Returns a success message or error.
    """
    try:
        with open(filename, "w") as f:
            f.write(code)
        return f"Successfully wrote code to {filename}"
    except Exception as e:
        return f"Error writing code: {e}"

@tool
def execute_generated_code(
    filename: Annotated[str, "File containing the code to import and run"],
    function_name: Annotated[str, "Name of the function to run"]
) -> str:
    """
    Dynamically imports 'filename', then calls the function 'function_name'(df).
    The function operates on a globally available DataFrame 'df'.
    """
    try:
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location("generated_module", filename)
        generated_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generated_module)

        # Check if the specified function exists in the module
        if not hasattr(generated_module, function_name):
            return f"Module does not have function '{function_name}'."
        
        # Get the function reference
        func = getattr(generated_module, function_name)

        # Ensure df exists in the global namespace
        if "df" not in globals():
            return "Global DataFrame 'df' not found. Ensure 'df' is defined before calling this tool."
        
        # Call the function with the global df
        global df  # Explicitly use the global DataFrame
        result = func(df)

        return f"Function '{function_name}' returned:\n{result}"
    except Exception as e:
        return f"Error executing code: {e}"

from langchain_core.tools import tool
import toolbox
import inspect

@tool
def search_toolbox() -> str:
    """
    Returns a JSON-serialized list of function names in toolbox.py 
    along with short docstrings, so the agent can see what's available.
    """
    result = []
    for name, obj in inspect.getmembers(toolbox, inspect.isfunction):
        # you could ignore private or special functions if needed
        if not name.startswith("_"):
            doc = (obj.__doc__ or "").strip()
            result.append({"function_name": name, "doc": doc})
    import json
    return json.dumps(result, indent=2)


@tool#(description="Executes an existing function from toolbox.py on the specified DataFrame by name.")
def execute_existing_code(
    function_name: Annotated[str, "Name of the existing function in toolbox.py to run"],
    df_name: Annotated[str, "Global DataFrame variable name to pass to the function"]
) -> str:
    """
    Looks up `function_name` in toolbox.py, retrieves the function,
    then calls it with the global DataFrame identified by `df_name`.

    Returns a string (summary or error).
    """
    # 1. Check if the function exists in toolbox
    if not hasattr(toolbox, function_name):
        return f"Error: toolbox.py has no function named '{function_name}'."

    func = getattr(toolbox, function_name)

    # 2. Check if the df_name exists in globals()
    if df_name not in globals():
        return f"Error: No global DataFrame found for id '{df_name}'."

    # 3. Retrieve the DataFrame
    df_obj = globals()[df_name]

    # 4. Call the function
    result = func(df_obj)
    return f"Function '{function_name}' returned:\n{result}"

# Put them in a tools list
tools = [search_toolbox, execute_existing_code, write_code_to_file, execute_generated_code]


# ---------------------------------------------------------------------------
# 2) CREATE THE LLM (ChatOpenAI) AND REACT AGENT
# ---------------------------------------------------------------------------
model = ChatOpenAI(
    openai_api_key=get_openai_api_key(),
    model_name="gpt-4",   # or "gpt-4o" if you have that model alias
    temperature=0
)

graph = create_react_agent(model, tools=tools)


# ---------------------------------------------------------------------------
# 3) HELPER TO PRINT THE STREAM
# ---------------------------------------------------------------------------
def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()



# ---------------------------------------------------------------------------
# 4) DEMO USAGE
# ---------------------------------------------------------------------------
if __name__ == "__main__":
 
    # Import Data File as Date Frame DF
    # df = pd.read_csv(f'Data/{data_file_name}') # Set Data as folder
    # data_file_name = "data.csv"
    # df = pd.read_csv(data_file_name)


    # Example user message:
    instructions = (
        #"Please fix any spelling errors in the data frame named df. After correcting spelling errors, 
        "Drop duplicate rows from the data frame named 'df' and return a summary of how many rows were removed, etc. "
        "You must first use the search_toolbox tool. If you find a function that you believe can complete the task, use the execute_existing_code tool to complete the task. "
        "If no existing function in toolbox.py can complete the task, "
        "then you must use the write_code_to_file and execute_generated_code tools to create a new Python function to complete the task. "
        "If a new function is created, save the function to a file named 'generated_toolbox.py'. Then, call the function to edit 'df'. "
        "Finally, display the data frame named 'df'."
    )

    inputs = {"messages": [("user", instructions)]}
    stream = graph.stream(inputs, stream_mode="values")
    print_stream(stream)
