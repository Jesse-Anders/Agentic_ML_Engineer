# Agentic_ML_Agent

 Agentic system that generates a data Pipeline for AI models

# The Journal<br>

##(For Nick and Jesse Capstone Only)<br>
                          

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

10pm - 1am<br>
Jesse Evening Coding Session.<br>
Added the following 2 Tools [coding_instructions, save_successful_code]. The instructions tools allows for detailed instructions on how to handle pythonic coding for the main ReAct agent when it must autonomously generate code. The save succesfull code is part of a set of functions that moves intitially generated code from a tool sandbox to a commited long term file that is accessed by the final generated_pipeline.py. Main instructions have been updated to be extremeleley explicit about task order of operations and handling the added tools.

### 1/16/25<br>

9-11:45pm<br>
Jesse Evening Coding Session.<br>
Cleaning file naming structure. Added code to grab name and descriptions from the lib_eda_static.py file and auto populate lib_eda_static_list.json file The lib_eda_static_list.json allows the LLM to search only tool names and descriptions of functions in a lib without having to poor over all the complete code of each function. Prepping data set for args parser...<br>
if __name__ == "_main_":
parser = argparse.ArgumentParser()
parser.add_argument('--dataset_path', type=str)
parser.add_argument('--pipeline_path', type=str, default=‘pipeline-py’) 
parser.add_argument('--static_edalib_path', type=str, default='static_edalib.py’)
parser.add_argument('--dynamic_edalib_path', type=str, default=‘dynamic_edalib.py’)
parser.add_argument('--11m_model', type=str, default=‘LM Studio Community/Meta-Llama-3-8B-Instruct-GGUF’)
parser.add_argument('--target_var', type-str)
args = parser.parse_args)

### 1/18/25<br>
4hr<br> 
Jesse Graphic Design Session<br>
Company name research and logo brainstorms, AI Dall-E designs and Photoshop design work.
![ferringrad-hex-rec](https://github.com/user-attachments/assets/27ba56ac-c653-4e23-aa4e-265d0c976bd3)

1/21/25<br>
Multisession Day<br>
1hr Meeting Prep<br>
1hr Meeting (Nick, Jesse, Daniyal, Fletcher)<br>
4hr Coding Session : Integrated task instruction directly into the LLM call via TASK_INST. <br>
Worked on updating and detailing the task instructions themselves. <br>
Detailed the generate code instruction CODE_INST<br> 
Put a place holder in for future code trouble shooting feature. Designed to help the LLM correct mistakes from its first coding attempt CODE_INSTR_TROUBLESHOOTING. <br>
Began work on the Task Creation Agent!

1/25/25<br>
2hr session<br>
Succesfully implemented state_modifier=TASK_INST, which allows a set of instructions to be appended to the task execution agent, which it uses to complete tasks.
<br><br>
Updated instructions to include a task completion confirmation check. The task execution agent genereates and runs code to confirm its task is complete.
<br><br>
Task Creation Agent Deployed! POORLY!<br>
Created a rudimentary single set of intructions to test what gpt4o mini can do when given broad freedom to  anylize the df and write a series of tasks based on its analysis. It is NOT GOOD at doing this. BUT, it functionally did create usable code and even added some usable tasks task_list.json.

1/26/25<br>
2pm-4pm 2h<br>
Jesse + Nick meeting 30 minutes + Brainstorm 1.5hr<br>
Prepped for new column iteration agent handling. Created data flow chart before building Column Iteration Agent<br><br>

8pm -12am 4h Coding Session<br>
Jesse Coding Session<br>
Created and deployed the Column Iteration Agent. This agent represents a new overall approach to the agentic system. One agent will handle all data Preprocessing in a column by column workflow that includes a drill-down-to-instructions methodology.<br>
This agent is now capable of determining data type and handling Integer & Float data preprocessing.<br><br>

1/26/27<br>
Afternoon 1hr Coding session<br>
Working towards handling alias nulls (NA, None, Missing, etc)<br><br>

Evening 3hr Coding Session<br>
Continued work on handling alias nulls and edge cases, when handling a numeric column with some limited text entries that are bad data, nulls, etc.<br><br>

1/28/25<br>
Evening 3hr Coding Session<br>
Completed the Column Object to Num and Alias Null Agent!<br>
This is the first column loop agent and it handles, a few critical tasks. It iterates over object columns only.<br>
1. The agent determines if the object column is truly object or in fact numeric. 90% numeric data columns have random junk text and mislabeled nulls all converted to proper nulls AND the column is converted to Foat or Int tpye<br>
2. The agent handles regular object/text columns and converts common mislabeled nulls to proper null type.<br>
3. Lastly the agent receives a list of the top 40 most common unique entries and determines if there are any remaining mislabeled nulls based on its own judgement.

