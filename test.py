from Supervisor import app
from Storytelling import story_agent
from improptu import impromptu_agent
from general import general_agent
from conflict import conflict_agent



## Instruction for using the testing of Supevisor agent
# You are to provide a list containing two elemets eg: ['Hello',"i would like to practice story telling"]    
def Supervisor_testing(input_list):
    a = input_list 
    from model import llm
    n = 0
    while n < 3:
        if n >= len(a):  
            break
        for step in app.stream(
            {"messages": [{"role": "user", "content": a[n]}]},
            stream_mode="values",
        ):
            latest = step["messages"][-1]
            response_content = latest.content
        if n == 1:
            result = llm.invoke(f"You are to provide an output based on the response it might be story ,imromptu speech or conflict {response_content}")
            a.append(result.content)
        if response_content is not None: 
            print(f"This is the{n+1} response {response_content}")
            n += 1  
        else:
            print("The code has misbehaved")
            break



## Instructions for testing of individual Agent testing
# This function will take agent and prompt as input
# agent input should be  'impromptu'/'Story'/'general'/'conflict' and the prompt should be a topic based on the agent you selected





def individual_agent_testing  (agent,prompt):
    agent_selection={'impromptu':impromptu_agent,
                     'Story':story_agent,
                     'general':general_agent,
                     'conflict':conflict_agent}
    
    for step in agent_selection[agent].stream(
        {"messages": [{"role": "user", "content": prompt}]},
            stream_mode="values",
        ):
        latest = step["messages"][-1]
        response_content = latest.content
    print(response_content)



    




