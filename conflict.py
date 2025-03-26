
from typing_extensions import Literal
from langgraph.graph import MessagesState,END,START,StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage
from model import llm




@tool
def analyze_conflict(conflict_scenario):
    """Analyze the conflict scenario and identify key issues, emotions, and miscommunication."""
    msg = llm.invoke(
        f"Analyze the following conflict scenario:\n{conflict_scenario}\n\n"
        "Things to do:\n"
            "Understand the senerio and check for diplomacy"
            "Feedback on Empathy\n"
            "Feedback on Assertiveness"
            
    )
    return msg.content




tools=[analyze_conflict]
llm_with_tools=llm.bind_tools(tools)
tools_by_name = {tool.name: tool for tool in tools}



def llm_call (state:MessagesState):
    """ LLM should use both the tools to analyze and evaluate the conflict resolution"""
    return {
        'messages':[
            llm_with_tools.invoke(
                [SystemMessage(content= "You are a conflict resolution expert. "
                    "You must analyze the conflict, evaluate the user's response, and assess the proposed resolution "
                    "by using the **Analyze the Conflict:\n")]
                    
                + state["messages"]
            )
        ]
    }

def tool_node(state:dict):
    """Performs tool call"""
    result=[]
    for tool_call in state["messages"][-1].tool_calls:

        tool=tools_by_name[tool_call['name']]
        observation=tool.invoke(tool_call['args'])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call['id']))
    return {"messages":result}    
    




# Define workflow
agent_builder =StateGraph(MessagesState)


# Add Nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("environment", tool_node)


# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_edge("llm_call","environment" )
agent_builder.add_edge("environment", END)
conflict_agent = agent_builder.compile(name='conflict_agent')