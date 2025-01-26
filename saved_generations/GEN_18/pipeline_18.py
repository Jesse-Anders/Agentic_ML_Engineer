
# generated_pipeline.py

# This file is intended to be a reusable data pipeline.

import pandas as pd

from pipeline_lib import *

df = pd.read_csv("data_inputs/data.csv", index_col=None)

df = fix_spelling_errors(df)
df = analyze_dataframe(df)
df = remove_duplicates(df)
analyze_dataframe(df)
df = handle_null_values(df)
df = analyze_null_handling(df)
df = review_data_types(df)
df = analyze_summary_statistics(df)
df = analyze_summary_statistics(df)
df = display_summary_statistics(analyze_summary_statistics(df))
df = handle_null_values(df)
df = analyze_null_handling(df)
df = review_data_types(df)
df = analyze_summary_statistics(df)
df = analyze_summary_statistics(df)
confirm_analysis_completed(analyze_summary_statistics(df)[0], analyze_summary_statistics(df)[1])
