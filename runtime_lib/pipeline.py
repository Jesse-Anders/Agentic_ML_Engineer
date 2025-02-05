
# generated_pipeline

# This file is intended to be a reusable data pipeline.

import pandas as pd

from static_lib import *
from pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)

df = evaluate_column_for_drop(df)
df = data_type_check(df)
df = evaluate_column_for_drop(df)
df = data_type_check(df)
df = data_type_check(df)
df = determine_numeric_or_categorical(df)
df = evaluate_outliers(df)
df = evaluate_imputation_strategy(df)
df = dynamic_stochastic_median_impute(df)
df = data_type_check(df)
df = determine_numeric_or_categorical(df)
df = evaluate_outliers(df)
df = evaluate_imputation_strategy(df)
df = dynamic_stochastic_median_impute(df)
