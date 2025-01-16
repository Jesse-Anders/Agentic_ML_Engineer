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
# 1) LOAD DATA INTO DATAFRAME DF
# ---------------------------------------------------------------------------
# Register a DataFrame
data_file_name = "data.csv"
df = pd.read_csv(data_file_name)

# ---------------------------------------------------------------------------
# 2) BUILD PIPELINE FILE
# ---------------------------------------------------------------------------
def initialize_pipeline_file():
    """
    Clears and resets the generated_pipeline.py file with boilerplate code.
    This ensures the pipeline starts fresh every time the agent system is called.
    """
    with open("generated_pipeline.py", "w") as pipeline_file:
        pipeline_file.write("# generated_pipeline.py\n")
        pipeline_file.write("# This file is automatically populated by the agentic system.\n")
        pipeline_file.write("# It is intended to be a reusable data pipeline.\n")
        pipeline_file.write("import pandas as pd\n\n")
        pipeline_file.write("import toolbox\n\n")
        pipeline_file.write("import generated_toolbox\n\n")
        pipeline_file.write('data_file_name = "data.csv"\n')
        pipeline_file.write("df = pd.read_csv(data_file_name)\n\n")
    print("generated_pipeline.py has been reset with boilerplate code.")

initialize_pipeline_file()

# ---------------------------------------------------------------------------
# 2) DEFINE TOOLS: "WRITE_CODE_TO_FILE" AND "EXECUTE_GENERATED_CODE"
# ---------------------------------------------------------------------------
@tool
def search_toolbox() -> str:
    """
    Returns a JSON-serialized list of available tools and their descriptions
    from the tool_list.json file.
    """
    try:
        # Load the tool list from the JSON file
        with open("tool_list.json", "r") as f:
            tools = json.load(f)

        # Validate the structure of the JSON file
        if not isinstance(tools, list) or not all("function_name" in tool for tool in tools):
            return "Error: Invalid format in tool_list.json. Each entry must include 'function_name'."

        return json.dumps(tools, indent=2)
    except FileNotFoundError:
        return "Error: tool_list.json not found. Ensure the file exists in the working directory."
    except Exception as e:
        return f"Error reading tool_list.json: {e}"


@tool
def execute_existing_code(
    function_name: Annotated[str, "Name of the function in toolbox.py to run"]
) -> str:
    """
    Executes the specified function from toolbox.py on the global DataFrame `df`.

    Assumes that `function_name` has been validated as existing in toolbox.py.

    Returns
    -------
    str
        A string containing the result of the function execution or an error message.
    """
    try:
        # Retrieve the function from toolbox.py
        func = getattr(toolbox, function_name)

        # Execute the function with the global DataFrame `df`
        result = func(df)

        # Append the function call to the pipeline file
        with open("generated_pipeline.py", "a") as pipeline_file:
            pipeline_file.write(f"toolbox.{function_name}(df)\n")

        return f"Function '{function_name}' executed successfully. Result:\n{result}"
    except NameError:
        return "Error: Global DataFrame 'df' not defined."
    except AttributeError:
        return f"Error: Function '{function_name}' not found in toolbox.py."
    except Exception as e:
        return f"Error: An unexpected error occurred while executing '{function_name}'. Details: {e}"


@tool
def write_code_to_file(
    code: Annotated[str, "The code to write into the file"]
) -> str:
    """
    Writes the provided 'code' to a file named 'generated_toolbox.py'.
    Overwrites if the file exists.
    Returns a success message or error.
    """
    try:
        # Fixed filename
        filename = "generated_toolbox.py"

        # Write the code to the fixed file
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
    The function operates on the global DataFrame 'df' directly.
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

        # Call the function with the global DataFrame 'df'
        result = func(df)

        # Append the function call to the pipeline file
        with open("generated_pipeline.py", "a") as pipeline_file:
            pipeline_file.write(f"generated_toolbox.{function_name}(df)\n")

        return f"Function '{function_name}' executed successfully. Result:\n{result}"
    except NameError:
        return "Error: Global DataFrame 'df' not defined. Ensure 'df' exists before calling this tool."
    except Exception as e:
        return f"Error executing code: {e}"


# ---------------------------------------------------------------------------
# 3) PUT TOOLS IN LIST
# ---------------------------------------------------------------------------
tools = [search_toolbox, execute_existing_code, write_code_to_file, execute_generated_code]

# ---------------------------------------------------------------------------
# 4) CREATE THE LLM (ChatOpenAI) AND REACT AGENT
# ---------------------------------------------------------------------------
model = ChatOpenAI(
    openai_api_key=get_openai_api_key(),
    model_name="gpt-4o",   # or "gpt-4o" if you have that model alias
    temperature=0
)

graph = create_react_agent(model, tools=tools)

# ---------------------------------------------------------------------------
# 5) HELPER TO PRINT THE STREAM
# ---------------------------------------------------------------------------
def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


# ---------------------------------------------------------------------------
# 6) DEMO USAGE
# ---------------------------------------------------------------------------

# Example user message:
instructions = (
    "Complete Tasks in Order and Use the 5 steps below to complete each task."
    "1.) Use the search_toolbox tool to find an appropriate function for the task. "
    "2.) Use the execute_existing_code tool to complete the task on the df. "
    "3.) If no existing function found with search_toolbox tool can complete the task, use the write_code_to_file to create a new Python function to complete the task. "
    "4.) If a new function is created, save the function to a file named 'generated_toolbox.py'. "
    "5.) Use the execute_generated_code tool to complete the task of the df. "

    "Task 1: Please fix any spelling errors in the data frame named df. " 
    "Task 2: Drop duplicate rows from the data frame named 'df' and return a summary of how many rows were removed, etc. "
    "Task 3: Save the data frame named df to a file named data_cleaned.csv "
)

inputs = {"messages": [("user", instructions)]}
stream = graph.stream(inputs, stream_mode="values")
print_stream(stream)
