AGENT2_1_IA = {
#=============================================================================================#
#    region                AGENT2_1   Redundancy Dictionary Execute                           #
#=============================================================================================#

    "AGENT2_1_START": (
        # This should actually be an LLM that reviews the Redundancy Dictionary and Updates the json first???
        "First, use exec_stored_func tool to run display_redundancy_json() without args. \n"
        "Then, call tool request_human_approval('clean_redundant_entries') \n"
        "If human grants approval, Use exec_stored_func tool to run clean_redundant_entries(df). \n"
        # "Use tool call get_inst(HUMAN_EXEC_INST) for further instructions."
        "END PROCESS."

    ),
    # Currently disabled to speed up run times.
    "HUMAN_EXEC_INST": (
        "Call tool request_human_exec. \n"
        "If human entered 'x', END PROCESS. \n" # Auto skips if arg.request_human is set to False
        "Else, keep calling tool request_human_exec to run each entered functions."
    ),

    # endregion
}
