from langgraph.graph import MessagesState,END,START,StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage,  ToolMessage,HumanMessage
from model import llm



@tool
def analyze_story_feedback(story):
    """Provide structured feedback on the story's structure, clarity, and engagement."""
    prompt=f"""
    Perform a short story analysis and critique with this structure:
    
    ## Narative Flow
    - Pacing evaluation
    - Plot progression
    - Scene transitions
    
    ## Vocabulary,
    - Readability score (1-10)
    - Vocabulary appropriateness
    - Coherence rating (1-10)
    
    ## Emotional impact.
    - Emotional impact score (1-10)
    - Reader investment potential
    - Memorability factors
    
    ## Improvement Suggestions
    
    
    Story: {story}
    """
    
    msg = llm.invoke(prompt)
    return msg.content



tools=[analyze_story_feedback]
llm_with_tools=llm.bind_tools(tools)
tools_by_name = {tool.name: tool for tool in tools}

    
def llm_call (state:MessagesState):
    """ For calling the tools in the llm"""
    return {
        'messages':[
            llm_with_tools.invoke(
                [SystemMessage(content="Use the tools in Analyze_story_feedback to analyze the story ")]
                + state["messages"]
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
agent_builder.add_edge("llm_call","environment" )
agent_builder.add_edge("environment", END)
story_agent = agent_builder.compile(name='story_agent')

