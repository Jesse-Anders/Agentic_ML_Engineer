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


def generate_llm_feature(df):
    """
    Iterates over each entry in the current column, uses the prebuilt React agent to generate a response ("fake" or "real"),
    and writes it to a new column named "<current_column>_gen_feature".
    """
    column = get_shared_var('current_column')
    target_column = column + "_gen_feature"
    
    prompt_template = (
        "Entry Text: {text}\n"
        "Read the following job Entry Text. If you think it is from a scam job posting, respond with 'fake'. "
        "Otherwise, respond with 'real'.\n"   
    )

    def call_agent_on_text(text: str) -> str:
        if pd.isna(text) or text.strip() == "":
            return ""
        
        prompt = prompt_template.format(text=text)
        inputs = {'messages': [{'role': 'user', 'content': prompt}]}
        
        try:
            assistant_response = ""
            # Process each event from the agent stream
            for event in basic_agent.stream(inputs):
                # Since event is always a dict with a "messages" key, we extract the last message
                if isinstance(event, dict) and "messages" in event:
                    assistant_response = event["messages"][-1].content.strip()
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