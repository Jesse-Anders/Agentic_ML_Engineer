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
        "Use the exec_stored_func to run generate_llm_feature_test.\n"
        # "Read get_inst(ABOUT_THE_TARGET) to understand the overall goal of this data set.\n"
        # "based on this goal, use the exec_stored_func tool to run ???\n"
        # "Use the exec_stored_func to run drop_column.\n"
        "END PROCESS"

    ),
            "ABOUT_THE_TARGET": (
        "The target variable for this data set is a bool (Real=0, Fake=1) that represenst whether a job posting is for a 'real' job or if the posting is scam, meaning it is a 'fake' job posting.\n"

    ),
    #endregion
}