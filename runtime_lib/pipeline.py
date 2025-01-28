
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)

df = data_type_check(df, 'col3')
df = determine_numeric_or_categorical(df, 'col3')
df = check_outliers_and_nulls(df, 'col3')
df = cap_outliers_and_impute_nulls(df, 'col3')
