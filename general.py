

from langgraph.graph import MessagesState,END,START,StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage
from model import llm



@tool
def introduction_tool(introduction):
    """You are an introduction chatbot guiding users to training exercises."""
    prompt=f"""
Role: Communication Coach with ability to decide the current input is greeting or some other request and direct them to the 
right type of reponse

    

    1  Impromptu:  
    → Provide topic ("Explain why remote work changes team dynamics")  
    → "You have 2 mins - begin when ready!"  

    2  Storytelling:  
    → Assign theme ("Share a tech adaptation story")  
    

    3 Conflict:  
    → Present scenario ("Colleague: 'You ignored my input'")  
    → "How would you respond?"  

    4 On greeting:
    "👋 Welcome! Practice:  
        1. Spoken responses 💬  
        2. Story crafting 📖  
        3. Conflict solutions ⚡  
        Choose a focus:" 

Current input: {introduction}  
"""


    
    msg = llm.invoke(prompt)
    return msg.content

tools=[introduction_tool]
llm_with_tools=llm.bind_tools(tools)
tools_by_name = {tool.name: tool for tool in tools}
        
def llm_call(state:MessagesState):
    """llm should use all the tools to analyze and evalute the """
    return{
        'messages':[
            llm_with_tools.invoke(
                [SystemMessage(content='You should select the tool introduction_tool for every message ')] 
                               + state['messages']

            )
        ]
    }


def tool_node(state:dict):
    """Performs tools call"""
    result=[]
    for tool_call in state['messages'][-1].tool_calls:
        tools=tools_by_name[tool_call['name']]
        observation=tools.invoke(tool_call['args'])
        result.append(ToolMessage(content=observation,tool_call_id=tool_call['id']))
      
    return {'messages':result}

agent_builder =StateGraph(MessagesState)



agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("environment", tool_node)


agent_builder.add_edge(START, "llm_call")
agent_builder.add_edge("llm_call","environment" )
agent_builder.add_edge("environment", END)
general_agent = agent_builder.compile(name='general_agent')

