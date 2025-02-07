import pandas as pd
import sys
import os
# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Shared State Getters
# from utils import get_dataframe_stage, get_target_column, get_current_column
from utils import get_dataframe_stage, get_target_column, get_current_column, print_stream


def show_sample_of_entries(df, sample_count=10):
    """
    Displays a random sample of sample_count=x rows from the specified column in the DataFrame.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The name of the column to sample from.
        
    Returns:
        pd.Series: A random sample of sample_count=x rows from the specified column.
    """
    column=get_current_column()
    return df[column].dropna().sample(n=min(sample_count, len(df)), random_state=42)




# lib.py
import pandas as pd
from tqdm import tqdm
from utils import get_agent3_1

def generate_llm_feature(df):
    """
    Iterates over each entry in 'nlp_column', uses the prebuilt React agent (agent3)
    to generate a concise one-word summary, and writes it to 'nlp_column_gen_feature'.
    """
    column=get_current_column()
    agent3_1 = get_agent3_1()
    target_column = column + "_gen_feature"
    
    prompt_template = (
        "Analyze the sentiment of the following text and summarize it in one word.\n"
        "Text: {text}\n"
        "Answer:"
    )
    
    def call_agent_on_text(text: str) -> str:
        if pd.isna(text) or text.strip() == "":
            return ""
        
        prompt = prompt_template.format(text=text)
        # If your agentic system uses these functions, update accordingly.
        #set_current_column(column)
        #pipeline.write(f'set_current_column("{column}")')
        
        inputs = {'messages': [('user', prompt)]}
        
        try:
            # Use the prebuilt agent3 from the shared module.
            stream = agent3_1.stream(inputs, stream_mode='values')
            response_text = ""
            for output in stream:
                response_text += str(output)
            response_text = response_text.strip()
            return response_text.split()[0] if response_text else ""
        except Exception as e:
            print(f"Error during agent stream for text: {text}\n{e}")
            return f"Error: {e}"
    
    tqdm.pandas(desc="Processing rows with agent")
    df[target_column] = df[column].progress_apply(call_agent_on_text)
    return df


# lib.py
import pandas as pd
from tqdm import tqdm

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
    column = get_current_column()
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
    column = get_current_column()
    
    # Ensure the column exists in the DataFrame.
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    
    # Drop the column (using inplace=False to return a new DataFrame)
    df = df.drop(columns=[column])
    print(f"Column '{column}' has been dropped from the DataFrame.")
    
    return df