
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)

df = data_type_check(df, 'col3')
df = check_percent_numeric(df, 'col3')
df = check_for_text_nums(df, 'col3')
df = convert_text_nums_to_numeric(df, 'col3')
df = describe_and_clean_non_numeric_entries(df, 'col3')
df = convert_review_list_entries_to_null(df, 'col3', review_list=['no data', 'data missing'])
