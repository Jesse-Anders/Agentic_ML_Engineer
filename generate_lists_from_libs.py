import ast
import json

def generate_name_descriptions_list(file_path, output_json):
    """
    Extracts function names and descriptions from a Python file and saves them to a JSON file.

    Args:
        file_path (str): Path to the Python file to parse.
        output_json (str): Path to the JSON file to save the output.
    """
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())

    function_list = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            docstring = ast.get_docstring(node)

            if docstring:
                # Extract the "description" from the docstring
                description_key = "\"description\":"

                description_value = ""

                for line in docstring.split('\n'):
                    line = line.strip()
                    if line.startswith(description_key):
                        description_value = line.split(':', 1)[1].strip().strip('"').strip(',')

                function_list.append({
                    "function_name": function_name,
                    "description": description_value
                })

    # Write the extracted data to a JSON file
    with open(output_json, 'w') as json_file:
        json.dump(function_list, json_file, indent=4)

# Example usage
generate_name_descriptions_list('toolbox.py', 'lib_eda_static_list.json')
