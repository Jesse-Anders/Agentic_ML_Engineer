
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from static_lib import *
from pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)

df = data_type_check(df, "col1")
df = determine_numeric_or_categorical(df, "col1")
df = evaluate_outliers(df, "col1")
df = evaluate_imputation_strategy(df, "col1")
df = dynamic_stochastic_median_impute(df, "col1")
df = data_type_check(df, "col2")
df = determine_numeric_or_categorical(df, "col2")
df = evaluate_outliers(df, "col2")
df = evaluate_imputation_strategy(df, "col2")
df = dynamic_stochastic_median_impute(df, "col2")
