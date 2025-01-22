
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from lib.static_lib import *
from lib.pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv")

fix_spelling_errors(df)
save_successful_code(df)
drop_df_duplicates(df)
