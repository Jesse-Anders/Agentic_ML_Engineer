import pandas as pd
import sys
import os
import json
from tqdm import tqdm
from agent_builds.base_agents import basic_agent

# NLP Libraries & Packages
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer


# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Shared State Getters
# from utils import get_dataframe_stage, get_target_column, get_current_column
from utils import get_dataframe_stage, get_shared_var, set_shared_var, print_stream


def gather_column_info(df, sample_count=10, sample_length=300):
    """
    Gathers and returns key information about the current column,
    such as data type, number of unique values, missing values,
    top value counts, a ratio of unique values to total rows,
    average entry length, and truncated samples.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the column.
    sample_count : int, optional
        Number of sample rows to retrieve.
    sample_length : int, optional
        Maximum number of characters to include for each sample value.

    Returns
    -------
    dict
        A dictionary containing column metadata useful for encoding decisions.
    """
    # Retrieve the current column from your shared variable system
    column = get_shared_var('current_column')

    # Validate column existence
    if column not in df.columns:
        return {
            "column_name": column,
            "error": f"Column '{column}' not found in DataFrame."
        }

    col_data = df[column]

    # Basic stats
    dtype = str(col_data.dtype)
    num_unique = col_data.nunique(dropna=True)
    total_rows = len(col_data)
    
    # Compute ratio of unique values to total rows
    unique_to_total_ratio = num_unique / total_rows if total_rows else 0.0

    # Compute average entry length (only for non-null entries)
    non_null_values = col_data.dropna().astype(str)
    average_entry_length = sum(len(entry) for entry in non_null_values) / len(non_null_values) if len(non_null_values) > 0 else 0

    # Top 5 value counts
    top_values_series = col_data.value_counts(dropna=False).head(5)
    top_values_dict = top_values_series.to_dict()

    # Sample data (truncated)
    sample_series = non_null_values.head(sample_count)
    truncated_samples = [val[:sample_length] for val in sample_series]

    # Construct the info dictionary
    column_info = {
        "Column Name": column,
        "Data Type": dtype,
        "Number of Unique Values": num_unique,
        "Total Rows": total_rows,
        "Ratio of Unique Entries to Total Entries (Lower Value Indicates More Likely Categorical)": unique_to_total_ratio,
        "Average Entry Length in Characters (Above 50 Indicates Very Likely NLP)": average_entry_length,
        "Top 5 Value Counts": top_values_dict,
        f"Sampling of Entries (length capped at {sample_length})": truncated_samples
    }

    return column_info

# Encode Categorical Features
def execute_numeric_encode(df, column):
    """
    Perform numeric encoding on a categorical column and update column_mappings.
    
    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    - column (str): The column to encode.
    - column_mappings (dict): The global dictionary to store encoding mappings.
    
    Returns:
    - pd.DataFrame: Updated DataFrame with numeric encoding.
    - dict: Updated column_mappings dictionary.
    """
    column_mappings = get_shared_var('column_mappings')
    
    # Check if the column exists in the DataFrame
    if column not in df.columns:
        print(f"Column '{column}' not found in DataFrame. Skipping...")
        return df, column_mappings  # Return without modification
    
    # Get unique values and sort them to ensure consistent mapping
    unique_values = sorted(df[column].dropna().unique())  # Drop NaN to avoid issues
    
    # Create a mapping dictionary from unique value to an integer code
    mapping_dict = {val: idx for idx, val in enumerate(unique_values)}
    
    # Create the encoded column name
    encoded_column_name = f'{column}_Numeric_Encoded'
    
    # Apply the mapping to create a new encoded column
    df[encoded_column_name] = df[column].replace(mapping_dict)
    
    # Drop the original column
    df.drop(columns=[column], inplace=True)
    
    # Update column_mappings dictionary
    column_mappings[encoded_column_name] = mapping_dict

    print(f"Created {encoded_column_name}")
    print(f"Encoded as {column_mappings[encoded_column_name]}")

    return df

# One Hot Encode Categorical Features for neural network models.
def execute_one_hot_encode(df, column):
    """
    Perform one-hot encoding on a categorical column.

    Parameters:
    - df (pd.DataFrame): The dataframe to modify.
    - column (str): The column to one-hot encode.

    Returns:
    - pd.DataFrame: Updated DataFrame with one-hot encoded features.
    """

    # Check if the column exists in the DataFrame
    if column not in df.columns:
        print(f"Column '{column}' not found in DataFrame. Skipping...")
        return df  # Return without modification
    
    # Identify unique non-null values in the column
    unique_values = sorted(df[column].dropna().unique())

    # For each unique category, create a new binary column
    new_columns = []
    for val in unique_values:
        new_col_name = f"{column}_one_hot_{val}"
        df[new_col_name] = (df[column] == val).astype(int)
        new_columns.append(new_col_name)

    # (Optional) Handle NaN values explicitly, if desired
    # e.g., if you want a separate column to indicate NaN
    # if df[column].isnull().any():
    #     nan_col_name = f"{column}_one_hot_nan"
    #     df[nan_col_name] = df[column].isnull().astype(int)
    #     new_columns.append(nan_col_name)

    # Drop the original column to mirror the style of execute_numeric_encode
    df.drop(columns=[column], inplace=True)

    print(f"One-hot encoded '{column}' → Created columns: {new_columns}")
    return df

# Ordinal Encode Columns with Data such as Small, Medium, Large.
def execute_ordinal_encode(df, column):
    """
    Perform ordinal encoding on a column that has already been deemed ordinal.
    Uses sorted unique values to assign an increasing integer code 
    (e.g., ['small', 'medium', 'large'] -> small=0, medium=1, large=2).

    Parameters:
    - df (pd.DataFrame): The DataFrame to modify.
    - column (str): The column to encode.

    Returns:
    - pd.DataFrame: The updated DataFrame with ordinal encoding.
    """
    # Retrieve the global column_mappings dictionary
    column_mappings = get_shared_var('column_mappings')

    # Check if the column exists in the DataFrame
    if column not in df.columns:
        print(f"Column '{column}' not found in DataFrame. Skipping...")
        return df  # Return without modification

    # Identify unique, non-null values in the column
    unique_values = df[column].dropna().unique()
    if len(unique_values) == 0:
        print(f"Column '{column}' has no non-null values. Skipping...")
        return df

    # Sort unique values for a simple (alphabetical or numeric) ordinal order
    sorted_unique_values = sorted(unique_values)

    # Create a mapping from each category to its ordinal rank
    mapping_dict = {val: idx for idx, val in enumerate(sorted_unique_values)}

    # Create the encoded column name
    encoded_column_name = f"{column}_Ordinal_Encoded"

    # Apply the mapping
    df[encoded_column_name] = df[column].replace(mapping_dict)

    # Drop the original column (mirroring the numeric encode approach)
    df.drop(columns=[column], inplace=True)

    # Update column_mappings with the new mapping
    column_mappings[encoded_column_name] = mapping_dict

    print(f"Created {encoded_column_name}")
    print(f"Ordinal mapping used: {column_mappings[encoded_column_name]}")

    return df


# MIN/MAX NORMALIZATION
# Creates a new Column with min/max normalization
def execute_scaling_normalization(df, column):
    """
    Apply min-max normalization to a specific column in a pandas DataFrame and create a new column for the normalized values.

    Parameters:
    - df: pandas DataFrame
    - column: The column to normalize

    The function will add a new column to the DataFrame with the normalized values, prefixed with 'mm_'.
    """

    # Apply min-max normalization
    min_value = df[column].min()
    max_value = df[column].max()
    df[column + '_Normalized'] = (df[column] - min_value) / (max_value - min_value)
    
        # Drop the original column
    df.drop(columns=[column], inplace=True)

    print(f"Created {column}_Normalized")

    return df


def execute_nlp_handler(df, column):
    '''
    Processes an NLP column through standard text preprocessing steps and creates vectorized features.
    
    Steps:
    1. Text preprocessing (lowercase, remove special chars, etc.)
    2. Tokenization and stop word removal
    3. TF-IDF vectorization with n-grams
    4. Add new features to dataframe with unique column names
    
    Args:
        df (pd.DataFrame): The dataframe containing the NLP column
        column (str): Name of the column to process
    
    Returns:
        pd.DataFrame: Updated dataframe with new NLP feature columns
    '''
    
    try: # Download all required NLTK resources
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('omw-1.4')  # Required for newer versions of NLTK
    except Exception as e:
        print(f"Error downloading NLTK resources: {e}")
    
    # Check if column exists
    if column not in df.columns:
        print(f"Column '{column}' not found in DataFrame. Skipping...")
        return df

    # Create a copy of the text column and fill NaN values
    text_series = df[column].fillna('')
    
    def preprocess_text(text):
        try:
            # Convert to string if not already
            text = str(text).lower()
            
            # Remove special characters and digits
            text = re.sub(r'[^a-zA-Z\s]', ' ', text)
            
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            try:
                tokens = word_tokenize(text)
            except Exception as e:
                print(f"NLTK tokenization failed: {e}. Falling back to simple split.")
                tokens = text.split()  # Fallback simple tokenization
            
            try:
                # Remove stopwords if available
                stop_words = set(stopwords.words('english'))
                tokens = [token for token in tokens if token not in stop_words]
            except Exception as e:
                print(f"Warning: Skipping stopword removal due to error: {e}")
            
            try:
                # Lemmatization if available
                lemmatizer = WordNetLemmatizer()
                tokens = [lemmatizer.lemmatize(token) for token in tokens]
            except Exception as e:
                print(f"Warning: Skipping lemmatization due to error: {e}")
            
            return ' '.join(tokens)
        except Exception as e:
            print(f"Warning: Error in preprocessing text: {e}")
            return str(text)  # Return original text as fallback
    
    # Apply preprocessing to all texts
    processed_texts = text_series.apply(preprocess_text)
    
    # TF-IDF Vectorization with n-grams
    vectorizer = TfidfVectorizer(
        max_features=1000,  # Limit number of features
        ngram_range=(1, 2),  # Include unigrams and bigrams
        min_df=2,  # Minimum document frequency
        max_df=0.95,  # Maximum document frequency
        token_pattern=r'(?u)\b\w+\b'  # Simple token pattern as fallback
    )
    
    try:
        # Fit and transform the processed texts
        tfidf_matrix = vectorizer.fit_transform(processed_texts)
        
        # Get feature names from vectorizer
        feature_names = vectorizer.get_feature_names_out()
        
        # Create unique column names for new features
        new_columns = [f"{column}_tfidf_{i}_{name}" for i, name in enumerate(feature_names)]
        
        # Convert sparse matrix to DataFrame with unique column names
        tfidf_df = pd.DataFrame(
            tfidf_matrix.toarray(),
            columns=new_columns,
            index=df.index
        )
        
        # Drop the original text column
        df = df.drop(columns=[column])
        
        # Concatenate the TF-IDF features with the original dataframe
        df = pd.concat([df, tfidf_df], axis=1)
        
        print(f"Processed NLP column '{column}' and created {len(new_columns)} new TF-IDF features")
        
    except Exception as e:
        print(f"Error in TF-IDF vectorization: {e}")
        return df  # Return original dataframe if vectorization fails
    
    return df