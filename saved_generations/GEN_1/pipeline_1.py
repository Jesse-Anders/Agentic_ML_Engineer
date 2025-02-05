
# generated_pipeline

# This file is intended to be a reusable data pipeline.

import pandas as pd

from static_lib import *
from pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)

df = evaluate_column_for_drop(df, "col1", "target")
df = data_type_check(df, "col1")
df = evaluate_column_for_drop(df, "col2", "target")
df = data_type_check(df, "col2")
# Column 'col2' has a data type of 'float64', which is not an object type.
