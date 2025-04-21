AGENT5_IA = {
#=============================================================================================#
#    region                AGENT5                                                             #
#=============================================================================================#
    "SUPER_AGENT5_START": (
        "Use get_pow_candidates('numeric') to recieve a 'compare' column and a list of parts-of-a-whole column candidates elligible for grouping.\n"
        "If there is a general or abstract grouping available for the 'compare' column, use the create_pow_group tool to create the group and END PROCESS."
    ),

    "AGENT5_START": (
        "Use the describe_pow_group tool to get a description of the parts-of-a-whole column group.\n"
        # Future: integrate data set goal for feature creation.
        "Consider the column group and write some code that will create a new valuable column from the group. The feature should hold new value in predicting the target variable of the dataset. Keep feature names concise and distinguishable.\n"
        "Use the test_pow_transform tool to execute the transformation code, the feature must not be redundant.\n"
        "If the transformation code is successful, END PROCESS.\n"
        # Future: store logic and information about newly created features to a file.
    )
    #endregion
}