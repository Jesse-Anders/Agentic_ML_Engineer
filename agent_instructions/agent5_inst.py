AGENT5_IA = {
#=============================================================================================#
#    region                AGENT5                                                             #
#=============================================================================================#
    "AGENT5_START": (
        "Tell me that you've read the Agent 5 instructions and END PROCESS.\n"
    ),
    "SUPER_AGENT5_START": (
        "Use get_pow_candidates('numeric') to recieve a list of parts-of-a-whole column groupings.\n"
        "Using chain-of-thought reasoning, examine the listed columns and classify them into parts-of-a-whole groups if any are sufficiently related."
        "Use the create_pow_groups tool to pass in your list of parts-of-a-whole column groupings and END PROCESS."
    )
    #endregion
}