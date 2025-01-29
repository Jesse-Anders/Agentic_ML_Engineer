
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
df = convert_'col3'_to_numeric(df, 'col3')
df = data_type_check(df, 'col4')
df = check_percent_numeric(df, 'col4')
df = convert_common_alias_nulls(df, 'col4')
df = display_most_common_unique_entries(df, 'col4')
df = convert_uncommon_alias_nulls(df, 'col4')
df = data_type_check(df, 'col1')
df = if_float_is_really_int_convert(df, 'col1')
df = determine_numeric_or_categorical(df, 'col1')
df = check_outliers_and_nulls(df, 'col1')
df = cap_outliers_and_impute_nulls(df, 'col1')
df = data_type_check(df, 'col2')
df = if_float_is_really_int_convert(df, 'col2')
df = determine_numeric_or_categorical(df, 'col2')
df = check_outliers_and_nulls(df, 'col2')
df = cap_outliers_and_impute_nulls(df, 'col2')
df = data_type_check(df, 'col3')
df = if_float_is_really_int_convert(df, 'col3')
df = determine_numeric_or_categorical(df, 'col3')
df = check_outliers_and_nulls(df, 'col3')
df = cap_outliers_and_impute_nulls(df, 'col3')
df = data_type_check(df, 'col4')
