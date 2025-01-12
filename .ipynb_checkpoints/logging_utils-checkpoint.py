# logging_utils.py

import json
import datetime
import os

def log_transformation(action_name):
    """
    Decorator that logs the result of a data transformation to a JSON file.
    The decorated function is expected to take a DataFrame as its first argument,
    but it can have additional arguments as needed.
    """
    def decorator(func):
        def wrapper(*args, log_file="transformations_log.json", session_id=None, **kwargs):
            # We assume the first argument is always a DataFrame
            df = args[0]
            initial_row_count = len(df)

            # Run the original function
            result_df = func(*args, **kwargs)

            # Calculate change in rows (if relevant)
            final_row_count = len(result_df)
            rows_changed = initial_row_count - final_row_count  # positive if rows are dropped

            # Build the log record
            action_record = {
                "action": action_name,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "parameters": {},  # Add any relevant parameters here
                "metadata": {
                    "initial_row_count": initial_row_count,
                    "final_row_count": final_row_count,
                    "rows_changed": rows_changed
                },
                "status": "success",
                "notes": ""
            }

            # Attach session/pipeline ID if provided
            if session_id is not None:
                action_record["session_id"] = session_id

            # Load or create the JSON log file
            try:
                with open(log_file, "r") as f:
                    existing_records = json.load(f)
                if not isinstance(existing_records, list):
                    existing_records = [existing_records]
            except (FileNotFoundError, json.JSONDecodeError):
                existing_records = []

            # Append the new record
            existing_records.append(action_record)

            # Write updated records back to the file
            with open(log_file, "w") as f:
                json.dump(existing_records, f, indent=2)

            return result_df

        return wrapper
    return decorator
