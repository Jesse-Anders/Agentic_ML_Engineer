import pandas as pd
import sys
import os
import json
from tqdm import tqdm
from agent_builds.base_agents import basic_agent

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Shared State Getters
# from utils import get_dataframe_stage, get_target_column, get_current_column
from utils import get_dataframe_stage, get_shared_var, print_stream


import pandas as pd

def show_sample_of_entries(df, sample_count=5, sample_length=1000):
    """
    Displays a random sample of sample_count rows from the specified column in the DataFrame,
    with each entry truncated to a maximum of sample_length characters.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        sample_count (int): The number of rows to sample.
        sample_length (int): The maximum number of characters displayed from each sample entry.

    Returns:
        pd.Series: A random sample of sample_count rows from the specified column, truncated.
    """
    column = get_shared_var('current_column')
    sampled_entries = df[column].dropna().sample(n=min(sample_count, len(df)), random_state=42)
    
    # Truncate each entry to the specified sample_length
    return sampled_entries.apply(lambda x: x[:sample_length] if isinstance(x, str) else x)



# def generate_llm_feature(df):
#     """
#     Iterates over each entry in the current column, uses the prebuilt React agent to generate a response to the prompt,
#     and writes it to a new column named "<current_column>_gen_feature".
#     """
#     column = get_shared_var('current_column')
#     target_column = column + "_gen_feature"
    
#     prompt_template = (
#         "Entry Text: {text}\n"
#         "call to a json list.\n"
#     )

#     def call_agent_on_text(text: str) -> str:
#         if pd.isna(text) or text.strip() == "":
#             return ""
        
#         prompt = prompt_template.format(text=text)
#         inputs = {'messages': [{'role': 'user', 'content': prompt}]}
        
#         try:
#             assistant_response = ""
#             # Process each event from the agent stream
#             for event in basic_agent.stream(inputs):
#                 # Since event is always a dict with a "messages" key, we extract the last message
#                 if isinstance(event, dict) and "messages" in event:
#                     assistant_response = event["messages"][-1].content.strip()
#             return assistant_response
#         except Exception as e:
#             print(f"Error during agent stream for text: {text}\n{e}")
#             return f"Error: {e}"

    
#     tqdm.pandas(desc="Processing rows with agent")
#     df[target_column] = df[column].progress_apply(call_agent_on_text)
#     return df




def generate_llm_feature(df):
    """
    Iterates over each entry in the current column and, for each prompt in the JSON file,
    uses the prebuilt React agent to generate a response. For each prompt, a new column is created:
    e.g., if the current column is "col6", the new columns will be "col6_gen_feature_1", "col6_gen_feature_2", etc.
    
    The JSON file (json_lib/nlp_fe_generated_prompts.json) should contain a list of prompt instructions.
    
    Example JSON structure:
    [
        "Generate a brief summary.",
        "Extract the key points.",
        "Rewrite the entry in plain language."
    ]
    """
    # Get the current column name and build the base target name.
    column = get_shared_var('current_column')
    base_target = column + "_gen_feature"
    
    # Load prompt instructions from JSON file.
    json_file = "json_lib/nlp_fe_generated_prompts.json"
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Cannot find the prompts file at {json_file}")
    
    with open(json_file, "r") as f:
        prompt_instructions = json.load(f)
    
    # Number of prompts to process.
    n_prompts = len(prompt_instructions)
    
    # Define a prompt template with placeholders for text and the prompt instruction.
    prompt_template = (
        "Entry Text: {text}\n"
        "Instruction: {prompt_item}\n"
    )

    def call_agent_on_text(text: str) -> list:
        # If text is empty, return a list of empty strings.
        if pd.isna(text) or text.strip() == "":
            return ["" for _ in range(n_prompts)]
        
        responses = []
        # Process each prompt instruction.
        for prompt_item in prompt_instructions:
            # Populate the prompt template.
            prompt = prompt_template.format(text=text, prompt_item=prompt_item)
            inputs = {'messages': [{'role': 'user', 'content': prompt}]}
            
            try:
                assistant_response = ""
                # Process each event from the agent stream.
                for event in basic_agent.stream(inputs):
                    # Extract the last message content.
                    if isinstance(event, dict) and "messages" in event:
                        assistant_response = event["messages"][-1].content.strip()
                responses.append(assistant_response)
            except Exception as e:
                print(f"Error during agent stream for text: {text} with prompt '{prompt_item}'\n{e}")
                responses.append(f"Error: {e}")
        return responses

    # Apply the function to the current column to get a Series of response lists.
    tqdm.pandas(desc="Processing rows with agent")
    response_series = df[column].progress_apply(call_agent_on_text)
    
    # Convert the Series of lists into a DataFrame.
    responses_df = pd.DataFrame(response_series.tolist(), index=df.index)
    # Rename each column to include the index (1-indexed).
    responses_df.columns = [f"{base_target}_{i+1}" for i in range(n_prompts)]
    
    # Merge the new columns into the original DataFrame.
    df = pd.concat([df, responses_df], axis=1)
    return df



