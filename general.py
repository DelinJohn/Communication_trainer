

from langgraph.graph import MessagesState,END,START,StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage
from model import llm



@tool
def introduction_tool(introduction):
    """You are an introduction chatbot guiding users to training exercises."""
    prompt=f"""
    Role: Introductory Training Facilitator
    Purpose: Engage users and guide them to specific practice scenarios in:
    1. 📖 Story Crafting & Narrative Analysis
    2. ⚡ Conflict Resolution Strategies
    3. 💬 Spontaneous Speaking Challenges

    Response Protocol:
    - For greetings: Combine welcome + value proposition + call to action
    

    Format Rules:
    → Maximum 2 sentences
    → Include clear next-step prompt
    

    Scenario Requirements:
    Storytelling: Ask the user to narrate a short story
    Conflict Resolution: Simulate a disagreement
    Impromptu Speaking: Prompt the user with a random topic
    make sure the topics you provide are not silly

    Examples:
    Impromptu Speaking:“Explain why teamwork is important”
    Conflict Resolution: “I’m upset becauseyou missed a deadline”
    Storytelling:"Ask the user to narrate "
    


    Current Input: {introduction}
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
                [SystemMessage(content='You should select the tool introduction_tool ')] 
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


# Add Nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("environment", tool_node)


# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_edge("llm_call","environment" )
agent_builder.add_edge("environment", END)
general_agent = agent_builder.compile(name='general_agent')

