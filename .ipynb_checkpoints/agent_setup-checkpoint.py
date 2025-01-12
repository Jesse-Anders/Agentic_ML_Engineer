# agent_setup.py

import os
import pandas as pd
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory

# Import your transformation function
from toolbox import drop_duplicate_rows

###############################################################################
# 1. Create the LangChain Tools
###############################################################################
drop_duplicate_rows_tool = Tool(
    name="drop_duplicate_rows",
    func=drop_duplicate_rows,
    description=(
        "Remove duplicate rows from a Pandas DataFrame. "
        "Logs the action to transformations_log.json."
    )
)

tools = [drop_duplicate_rows_tool]

###############################################################################
# 2. Configure the LLM
###############################################################################
# Make sure to set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_KEY_HERE"

llm = OpenAI(
    temperature=0,
    openai_api_key=os.environ["OPENAI_API_KEY"]
)

###############################################################################
# 3. Build an Agent
###############################################################################
template = """You are a data-cleaning AI. 
You have access to these tools:
{tools}

When you decide on a tool, use the format:
Thought: reason about which tool to use Action: <tool name> Action Input: <input for the tool>
When you have a final answer, respond with:
Final Answer: <what the user wants to see>

{history}
User Query: {input}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["history", "input", "tools"]
)

memory = ConversationBufferMemory(memory_key="history")

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prompt=prompt,
    memory=memory
)

###############################################################################
# 4. Example Usage
###############################################################################
if __name__ == "__main__":
    # Create a mock DataFrame
    df = pd.DataFrame({
        "col1": [1,1,2,2,3,3],
        "col2": ["A","A","B","B","C","C"]
    })

    # The agent won't automatically know about `df` since it's Python-only object,
    # but let's illustrate how you'd call the tool directly in your code:
    cleaned_df = drop_duplicate_rows(df, session_id="pipeline_run_001")

    print("Data after dropping duplicates:")
    print(cleaned_df)

    # Or if you want the LLM to reason about calling this tool,
    # you might prompt it:
    user_query = "We have a dataset with duplicates. Please remove duplicates."
    response = agent.run(input=user_query)
    print("\nAgent final response:\n", response)
