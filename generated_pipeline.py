# generated_pipeline.py
# This file is automatically populated by the agentic system.
# It is intended to be a reusable data pipeline.
import pandas as pd

import lib_eda_static

import generated_toolbox_saved

data_file_name = "data.csv"
df = pd.read_csv(data_file_name)

lib_eda_static.drop_df_duplicates(df)
lib_eda_static.save_df_to_csv(df)
