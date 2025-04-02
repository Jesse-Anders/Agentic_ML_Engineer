AGENT2_1_IA = {
#=============================================================================================#
#    region                AGENT2_1   Redundancy Dictionary Execute                           #
#=============================================================================================#

    "AGENT2_1_START": (
        # This should actually be an LLM that reviews the Redundancy Dictionary and Updates the json first???
        "Use Use exec_stored_func tool to run populate_redundancy_json \n"
        "Use exec_stored_func tool to run display_redundancy_json().\n"
        "Call tool request_human_approval('clean_redundant_entries')\n"
        "If human grants approval, Use exec_stored_func tool to run clean_redundant_entries(df).\n"
        "Else, END PROCESS."
    ),

    # endregion
}
