# endregion
#=============================================================================================#
# region                                AnalyticsRunner                                       #
#=============================================================================================#

class AnalyticsRunner:
    def __init__(self, args, df):
        self.args = args
        
        self.original_df = df.copy()
        self.backup_df = df.copy()
        self.df = df.copy()

    def get_df(self):
        '''
        Return current df
        '''
        return self.df
    
    def set_df(self, df):
        '''
        Reassigns all dataframe variables
        '''
        self.original_df = df.copy()
        self.backup_df = df.copy()
        self.df = df.copy()

    def run(self):
        '''
        Executes feature engineering logic
        '''
        return self.df
    

#=======================================================#
#           Task Creation Agent                   #
#=======================================================#


# # for entry in ANALYTICS:
# inputs = {'messages': [('user', ANALYTICS_INSTR)]}

# try:
#     # feed the task list into the execution agent
#     stream = task_creation_agent.stream(inputs, stream_mode='values')
#     print_stream(stream)
# except Exception as e:
#     print(f'Error during stream: {e}')

# #return the most recent df
# return self.df


#=======================================================#
#        Execution from task_list.json Jand     #
#=======================================================#       

# # Load tasks from task_list.json
# with open(f'{JSON_DIR}/{TASK_LIST}.json', "r") as file:
#     tasks = json.load(file)

# # Iterate over each task in the JSON file
# for task in tasks:

#     # Construct inputs with global instructions and the task
#     inputs = {'messages': [('user', f"Task: {task['task']}")]}

#     try:
#         # Feed the task list into the execution agent
#         stream = preprocessor_agent.stream(inputs, stream_mode='values')
#         print_stream(stream)
#     except Exception as e:
#         print(f'Error during stream: {e}')

# # Return the most recent dataframe (assuming it's updated elsewhere in the class)
# return self.df