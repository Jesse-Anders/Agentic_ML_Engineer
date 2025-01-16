# Agentic_ML_Agent
 Agentic system that generates a data Pipeline for AI models

# The Journal<br>
(For Nick and Jesse Capstone)<br>
                          

### 1/14/2025<br>
1pm - 2:30pm. <br>
First in person meeting: Dicussed project plans 1hr. Nick helped outline and explain forward feed functions in the ADAS ARC code, deepened understanding of ADAS code and edges.

9pm - 12am <br>
Jesse Evening Study Session.<br>
Deepdive into LangGraph capabilities.<br> 
Complete Readthrough https://langchain-ai.github.io/langgraph/tutorials/introduction/<br>
Deepend understand of states, nodes, edges, memory, time travel, etc.<br>
Concepts to Further Study and Employ: Human in The Loop. Give LLM agency to decide to bring human into the loop.<br> 
<b>Create ReAct agent from scratch</b> https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/<br>
Might want to rebuild the current pre-built ReAct agent to handle human in the loop and give pre-prompted workflow instructions to the agent.<br>

### 1/15/25<br>
10pm - 1am
Jesse Evening Coding Session.<br>
Added the following 2 Tools [coding_instructions, save_successful_code]. The instructions tools allows for detailed instructions on how to handle pythonic coding for the main ReAct agent when it must autonomously generate code. The save succesfull code is part of a set of functions that moves intitially generated code from a tool sandbox to a commited long term file that is accessed by the final generated_pipeline.py. Main instructions have been updated to be extremeleley explicit about task order of operations and handling the added tools.
