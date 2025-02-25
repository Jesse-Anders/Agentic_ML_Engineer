AGENT6_IA = {
#=============================================================================================#
#    region                AGENT6                                                             #
#=============================================================================================#
    "AGENT6_START": (
        # "Use the encode_choice tool to add the current column to the encode_selections dictionary as Encode_Categorical_Features.\n"
        "There are 6 options and your task is to determine which of the 6 encoding processes should be executed on the current column.\n"
        ""
        "END PROCESS.\n"
    ),
    #endregion
}

# encode_selections = {
#     'Numeric_Encode_Categorical_Features': [],
#     'One_Hot_Encode_Categorical_Features': [],
#     'Boolean_Encode_Categorical_Features': [],
#     'MinMax_Normalize': [],
#     'NLP_Features':[],
#     'Bin_Numeric': []  # For Bin_Numeric, we'll store tuples: (column, n_bins)
#     }   



# Example “Recommended Encodings” Lists
# Tree-Based Models
# 1.	Numeric (Label) Encode (for most categorical features).
# 2.	Ordinal Encoding (if the data is genuinely ordinal).
# 3.	Frequency/Count Encoding (if cardinality is high).
# 4.	Boolean Encode by Threshold (optional, if you want to turn a multi-category feature into a single important/less-important feature).
# 5.	NLP for text columns.
# 6.	Scaling/Normalization (less critical, typically optional, unless you have hybrid pipelines that also feed into an algorithm that needs scaling).
# Neural Networks / Linear Models
# 1.	One-Hot Encode (for small/medium cardinality nominal features).
# 2.	Ordinal Encoding (if genuinely ordinal).
# 3.	Frequency/Count Encoding (for high-cardinality nominal features).
# 4.	Boolean Encode by Threshold (could still be used, but less common).
# 5.	NLP for text columns (could be embeddings or TF-IDF, depending on approach).
# 6.	Scaling/Normalization (almost always recommended—Min/Max or Standard Scaling for numeric features).
