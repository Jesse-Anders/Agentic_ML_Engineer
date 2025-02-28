AGENT3_IA = {
#=============================================================================================#
#    region                AGENT3                                                             #
#=============================================================================================#
    "AGENT3_START": (
        "Use the exec_stored_func to run show_sample_of_entries to show a sampling of entries in the column.\n" # Can ask LLM to set arg value of sample_count to something like 30 if you want
        "Use your judgement to decide if the entries represent natural language processing 'NLP' data.\n"
        #"If you deem the column to be an 'NLP' column of data, use the add_nlp_column tool to add the column name to the NLP column list.\n"
        "If you deem the column to be an 'NLP' column of data, use the tool call get_inst(NLP_INST) for instructions.\n"
        "If the entries are not NLP, meaning single words, extremely short entries, etc, END PROCESS."

    ),
    "NLP_INST": (
        "Call get_inst('DATA_SET_GOAL') to understand the overall goal of this data set.\n"
        # "Use exec_stored_func tool to run show_sample_of_entries to get an overall feel for the text entries in the current column.\n"
        # "Based on the goal of this data set and the overall feel of the text entries in current column, your task is to create 4 text prompts for an LLM.\n"
        # "Each prompt should begin with 'Based on the Entry Text' and each prompt should make clear that the result must contain only one word.\n"
        # "Your prompts should be dissimilar and each prompt should attempt to draw unique and valuable attibutes from the entry text."
        # "Use the append_to_json_list tool with json_path as 'json_lib/nlp_fe_generated_prompts.json' to save your new prompts.\n"
        "Use the exec_stored_func to run generate_llm_feature.\n"
        "END PROCESS"

    ),
    "DATA_SET_GOAL": (), # blank by intention, handled in main.py in the get_inst tool
    "EXAMPLE_PROMPTS": (
        "EXAMPLE PROMPT 1.) Read the following Entry Text. If you think it is from a scam job posting, respond with 'fake'. Otherwise, respond with 'real'."
        "EXAMPLE PROMPT 2.) Read the following Entry Text. Determine the sentiment of the text and output one of the following one word answers... 'happy', 'angry', 'sad', 'non-emotive'."
    ),
    # Instructions for creating a well-formatted JSON list of alias nulls.
    "JSON_PROMPT_LIST_INST": (
        "Here is a simple example of a well-formatted JSON list:\n"
        '[ "Prompt 1 would go here", "A second prompt would be here", "and so on"]\n'
        "Ensure that:\n"
        "1. Each entry is a string enclosed in double quotes.\n"
        "2. Entries are separated by commas.\n"
        "3. No trailing commas after the last item.\n"
        "4. Each item in the list should be a complete prompt and instruct the LLM exactly how to complete its objective.\n"
        "5. The list must be valid JSON format.\n"
    ),
    #endregion
}