
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)

df = data_type_check(df, column)
df = if_float_is_really_int_convert(df, column)
df = determine_numeric_or_categorical(df, column)
df = check_outliers_and_nulls(df, column)
df = cap_outliers_and_impute_nulls(df, column)
df = data_type_check(df, column)
df = if_float_is_really_int_convert(df, 'col2')
df = determine_numeric_or_categorical(df, 'col2')
df = check_outliers_and_nulls(df, 'col2')
df = cap_outliers_and_impute_nulls(df, 'col2')
df = data_type_check(df, column)
df = determine_numeric_or_categorical(df, 'col3')
df = check_outliers_and_nulls(df, 'col3')
df = cap_outliers_and_impute_nulls(df, 'col3')
