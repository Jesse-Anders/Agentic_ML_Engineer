
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)

df = data_type_check(df, 'col4')
df = check_percent_numeric(df, 'col4')
df = convert_common_alias_nulls(df, 'col4')
df = display_most_common_unique_entries(df, 'col4')
df = convert_uncommon_alias_nulls(df, 'col4')
