import pandas as pd
import sys
import os
from tqdm import tqdm
from agent_builds.base_agents import basic_agent

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Shared State Getters
# from utils import get_dataframe_stage, get_target_column, get_current_column
from utils import get_dataframe_stage, get_shared_var, print_stream


def show_sample_of_entries(df, sample_count=10):
    """
    Displays a random sample of sample_count=x rows from the specified column in the DataFrame.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The name of the column to sample from.
        
    Returns:
        pd.Series: A random sample of sample_count=x rows from the specified column.
    """
    column=get_shared_var('current_column')
    return df[column].dropna().sample(n=min(sample_count, len(df)), random_state=42)




# lib.py
import pandas as pd
from tqdm import tqdm

# def generate_llm_feature(df):
#     """
#     Iterates over each entry in 'nlp_column', uses the prebuilt React agent (agent3)
#     to generate a concise one-word summary, and writes it to 'nlp_column_gen_feature'.
#     """
#     column=get_current_column()
#     agent3_1 = get_agent('agent3_1')
#     target_column = column + "_gen_feature"
    
#     prompt_template = (
#         "Read following job description text. If you think it is from a scam job posting, respond with 'fake'. Otherwise, respond with 'real'.\n"
#         "Job Description Text: {text}"
#     )
    
#     def call_agent_on_text(text: str) -> str:
#         if pd.isna(text) or text.strip() == "":
#             return ""
        
#         prompt = prompt_template.format(text=text)
#         # If your agentic system uses these functions, update accordingly.
#         #set_current_column(column)
#         #pipeline.write(f'set_current_column("{column}")')
        
#         inputs = {'messages': [('user', prompt)]}
        
#         try:
#             # Use the prebuilt agent3 from the shared module.
#             stream = agent3_1.stream(inputs, stream_mode='values')
#             response_text = ""
#             for output in stream:
#                 response_text += str(output)
#             response_text = response_text.strip()
#             return response_text.split()[0] if response_text else ""
#         except Exception as e:
#             print(f"Error during agent stream for text: {text}\n{e}")
#             return f"Error: {e}"
    
#     tqdm.pandas(desc="Processing rows with agent")
#     df[target_column] = df[column].progress_apply(call_agent_on_text)
#     return df


def generate_llm_feature(df):
    """
    Iterates over each entry in the current column, uses the prebuilt React agent to generate a response ("fake" or "real"),
    and writes it to a new column named "<current_column>_gen_feature".
    """
    column = get_shared_var('current_column')
    target_column = column + "_gen_feature"
    
    prompt_template = (
        "Read the following job description text. If you think it is from a scam job posting, respond with 'fake'. "
        "Otherwise, respond with 'real'.\n"
        "Job Description Text: {text}"
    )

    def call_agent_on_text(text: str) -> str:
        if pd.isna(text) or text.strip() == "":
            return ""
        
        prompt = prompt_template.format(text=text)
        inputs = {'messages': [{'role': 'user', 'content': prompt}]}
        
        try:
            assistant_response = ""
            # Loop over each event in the stream
            for event in basic_agent.stream(inputs):
                # Debug print to inspect what the event looks like:
                # print("DEBUG event:", event)
                
                # Case 1: event is a dict that contains "messages"
                if isinstance(event, dict) and "messages" in event:
                    # Assume event["messages"] is a list and the last element is the assistant message
                    assistant_response = event["messages"][-1].content.strip()
                
                # Case 2: event is a dict but doesn't directly have "messages"
                # In this case, iterate over its values
                elif isinstance(event, dict):
                    for key, value in event.items():
                        # If the value is a dict with "messages", extract it.
                        if isinstance(value, dict) and "messages" in value:
                            assistant_response = value["messages"][-1].content.strip()
                        # If the value is a list, iterate over its items.
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict) and "messages" in item:
                                    assistant_response = item["messages"][-1].content.strip()
                
                # Case 3: event is directly a list of items
                elif isinstance(event, list):
                    for item in event:
                        if isinstance(item, dict) and "messages" in item:
                            assistant_response = item["messages"][-1].content.strip()
                
                # Case 4: event is simply a string (this can happen in some modes)
                elif isinstance(event, str):
                    assistant_response = event.strip()
            
            return assistant_response
        except Exception as e:
            print(f"Error during agent stream for text: {text}\n{e}")
            return f"Error: {e}"




    
    tqdm.pandas(desc="Processing rows with agent")
    df[target_column] = df[column].progress_apply(call_agent_on_text)
    return df





def generate_llm_feature_test(df):
    """
    A test function that iterates over each entry in the current column
    (as determined by get_current_column()), extracts the first 5 characters
    of the text, and writes the result into a new column whose name is the
    current column name with '_gen_feature' appended.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame containing the text column.
    
    Returns:
        pd.DataFrame: The DataFrame updated with a new column containing the
                      first 5 characters of each entry from the original column.
    """
    # Get the current column name. Make sure get_current_column is available.
    column = get_shared_var('current_column')
    target_column = column + "_gen_feature"
    
    def first_five_chars(text: str) -> str:
        if pd.isna(text) or not text:
            return ""
        return text[:5]
    
    tqdm.pandas(desc="Processing rows")
    df[target_column] = df[column].progress_apply(first_five_chars)

    return df


def drop_column(df):
    """
    Drops a specified column from the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame from which the column will be dropped.
        column (str): The name of the column to drop.

    Returns:
        pd.DataFrame: The DataFrame with the specified column removed.
    """
    column = get_shared_var('current_column')
    
    # Ensure the column exists in the DataFrame.
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    
    # Drop the column (using inplace=False to return a new DataFrame)
    df = df.drop(columns=[column])
    print(f"Column '{column}' has been dropped from the DataFrame.")
    
    return df