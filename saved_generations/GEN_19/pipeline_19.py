
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)

df = data_type_check(df, 'col3')
df = check_percent_numeric(df, 'col3')
df = check_for_text_nums(df, 'col3')
df = convert_text_nums_to_numeric(df, 'col3')
df = data_type_check(df, 'col2')
df = if_float_is_really_int_convert(df, 'col2')
df = determine_numeric_or_categorical(df, 'col2')
df = check_outliers_and_nulls(df, 'col2')
df = cap_outliers_and_impute_nulls(df, 'col2')
