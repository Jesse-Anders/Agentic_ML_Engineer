
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from static_lib import *
from pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)

df = check_percent_numeric(df, 'col3')
df = check_for_text_nums(df, 'col3')
df = convert_text_nums_to_numeric(df, 'col3')
df = convert_'col3'_to_numeric(df, 'col3')
df = check_percent_numeric(df, 'col5')
df = check_for_text_nums(df, 'col5')
df = convert_'col5'_to_numeric(df, 'col5')
