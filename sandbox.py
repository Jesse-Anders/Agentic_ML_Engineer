# Sandbox for testing code snippets

with open("generated_pipeline.py", "a") as pipeline_file:
    # pipeline_file.write(f"# From {filename}\n")
    pipeline_file.write(f"toolbox.drop_df_duplicates(df)\n")