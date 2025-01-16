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
        pipeline_file.write("import generated_toolbox_saved\n\n")
        pipeline_file.write('data_file_name = "data.csv"\n')
        pipeline_file.write("df = pd.read_csv(data_file_name)\n\n")
    print("generated_pipeline.py has been reset with boilerplate code.")

initialize_pipeline_file()

# ---------------------------------------------------------------------------
# 2) DEFINE TOOLS: "GENERATE_CODE" AND "EXECUTE_GENERATED_CODE"
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
def coding_instructions() -> str:
    """
    Provides detailed guidance for writing new Python functions.
    Use this tool only when no pre-existing function meets the task requirements.
    """
    return (
        "When writing new Python functions, follow these guidelines:\n"
        "- employ textblob when handling spelling errors.\n"
        "- Ensure the function is Pythonic, efficient, and handles edge cases.\n"
        "- Include inline comments explaining the logic and any assumptions.\n"
        "- Test the function with realistic inputs to ensure correctness.\n"
        "- Use descriptive variable names to make the code readable.\n"
        "- Avoid hardcoding values; make the function reusable when possible.\n"
        "- Structure the code logically, with clear input and output specifications.\n"
    )

@tool
def generate_code(
    code: Annotated[str, "The code to write into the file"]
) -> str:
    """
    Writes the provided 'code' to a file named 'generated_toolbox_sandbox.py'.
    Overwrites if the file exists.
    Returns a success message or error.
    """
    try:
        # Fixed filename
        filename = "generated_toolbox_sandbox.py"

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
        #with open("generated_pipeline.py", "a") as pipeline_file:
        #    pipeline_file.write(f"generated_toolbox_sandbox.{function_name}(df)\n")

        return f"Function '{function_name}' executed successfully. Result:\n{result}"
    except NameError:
        return "Error: Global DataFrame 'df' not defined. Ensure 'df' exists before calling this tool."
    except Exception as e:
        return f"Error executing code: {e}"

@tool
def save_successful_code():
    """
    Appends the content of 'generated_toolbox_sandbox.py' to 'generated_toolbox_saved.py'.
    Use this tool after verifying that the generated code in 'generated_toolbox_sandbox.py' 
    has been successfully executed and works as expected.
    """
    generated_file = "generated_toolbox_sandbox.py"
    saved_file = "generated_toolbox_saved.py"

    try:
        # Read the content of generated_toolbox_sandbox.py
        with open(generated_file, "r") as gen_file:
            generated_code = gen_file.read()

        # Append the content to generated_toolbox_saved.py
        with open(saved_file, "a") as save_file:
            save_file.write("\n\n# --- Successfully Generated Code ---\n")
            save_file.write(generated_code)
# FUNCTION_NAME IS NOT DEFINED YET IN THE GENERATED FUNCTION IN ORDER TO UPDATE GENERATED_PIPELINE
                # Append the function call to the pipeline file
        #with open("generated_pipeline.py", "a") as pipeline_file:
        #    pipeline_file.write(f"generated_toolbox_saved.{function_name}(df)\n")

        return f"Code from '{generated_file}' has been successfully appended to '{saved_file}'."

    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# ---------------------------------------------------------------------------
# 3) PUT TOOLS IN LIST
# ---------------------------------------------------------------------------
tools = [search_toolbox, execute_existing_code, coding_instructions, generate_code, execute_generated_code, save_successful_code]

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
    "Complete each task strictly in numerical order, starting with Task 1, followed by Task 2, and so on. Finish each task fully before starting the next. "
    "Task 1: Please fix any spelling errors in the data frame named df. " 
    "Task 2: Drop duplicate rows from the data frame named 'df' and return a summary of how many rows were removed, etc. "
    "Task 3: Save the data frame named df to a file named data_cleaned.csv "

    "Use the 5 steps below to complete each individual task.\n"
    "1.) Use the search_toolbox tool to find an appropriate function for the task.\n"
    "2.) Use the execute_existing_code tool to complete the task on the df.\n"
    "3.) If, and only if, no appropriate function is found to complete the task, proceed as follows. "
    "   a) Use the coding_instructions tool to retrieve detailed guidelines for writing the function.\n"
    "   b) Write a Pythonic function based on the instructions provided.\n"
    "   c) Use the write_code_to_file tool to save the function.\n"
    "   d) Use the execute_generated_code tool to apply the function to the data frame.\n"
    "   e) If the generated code executes successfully, run the save_successful_code tool.\n"

)

inputs = {"messages": [("user", instructions)]}
stream = graph.stream(inputs, stream_mode="values")
print_stream(stream)
