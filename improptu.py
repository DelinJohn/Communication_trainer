
from typing_extensions import Literal
from langgraph.graph import MessagesState,END,START,StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage

from model import llm



@tool
def analyze_speech_structure(response):
    """Evaluates the structure of the response (logical flow, coherence, and transitions)."""
    msg = llm.invoke(
        f"Analyze the following impromptu speech response:\n{response}\n\n"
        "Evaluate the structure based on:\n"
        "1. Logical flow (Does it have a clear introduction, body, and conclusion?)\n"
        "2. Structure \n"
        "3. clarity\n"
        "4. Engagement."
    )
    return msg.content






tools=[analyze_speech_structure]
llm_with_tools=llm.bind_tools(tools)
tools_by_name={tool.name:tool for tool in tools}


def llm_call(state:MessagesState):
    """llm should use all the tools to analyze and evalute the """
    return{
        'messages':[
            llm_with_tools.invoke(
                [SystemMessage(content="""\
You are a rigorous impromptu speaking coach. Analyze user responses in 3 steps:

1. **Structural Analysis** - Use 'analyze_speech_structure' to examine:
   - Introduction/Body/Conclusion flow
   - Logical transitions between ideas
   - Overall organizational effectiveness
\
""")] 
                               + state['messages']

            )
        ]
    }

def tool_node(state:dict):
    """Perform tools call"""
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

agent_builder.add_edge("llm_call","environment")
agent_builder.add_edge("environment",END)
impromptu_agent = agent_builder.compile(name='impromptu_agent')


