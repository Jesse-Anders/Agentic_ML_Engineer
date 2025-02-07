import pandas as pd
# Add the project root directory to sys.path
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Shared State Getters
from utils import get_dataframe_stage, get_target_column, get_current_column


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

