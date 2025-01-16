# generated_pipeline.py
# This file is automatically populated by the agentic system.
# It is intended to be a reusable data pipeline.
import pandas as pd

import toolbox

import generated_toolbox

data_file_name = "data.csv"
df = pd.read_csv(data_file_name)

toolbox.drop_df_duplicates(df)
toolbox.save_df_to_csv(df)
