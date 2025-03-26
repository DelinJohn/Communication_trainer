from langgraph.graph import MessagesState,END,START,StateGraph
from typing_extensions import Literal, TypedDict
from langchain_core.messages import HumanMessage
from langgraph.types import Command








from Storytelling import story_agent
from conflict import conflict_agent
from improptu import impromptu_agent
from general import general_agent
from model import llm















members=["story_agent","conflict_agent","impromptu_agent","general_agent"]


system_prompt = (
    """
   Core Purpose
    Route user queries to specialized agents based on content type, maintaining natural conversational flow.

Agent Network


    </Story Agent>
    Story Agent
    Trigger: User shares a complete story/segment for analysis.
    Check for:
        Multi-sentence narrative structure
        Contains characters, plot development, or setting descriptions
        Exclude: Requests for topics/help ("Can you give me a story prompt?")
    </Story Agent>

    </Conflict Agent>
    Conflict Agent
    Trigger: User describes a conflict scenario for resolution analysis.
    Check for:
        Multi-sentence context
        Identifies involved parties + core disagreement
        Mentions attempted resolutions
        Exclude: General advice requests ("How do I handle conflicts better?")
    </Conflict Agent>

    </Impromptu Agent>
    Impromptu Agent
    Trigger: User delivers/practices spontaneous speech content.
    Check for:
        Speech structure (intro, body, conclusion)
        Time limits or format constraints
        Exclude: Requests for speech tips or templates
    </Impromptu Agent>


    </General Agent>
    General Agent
    Trigger: All single liner and also Help requests interactions
    Handles:
        Help requests ("I need to practice storytelling")
        Topic/prompt generation ("Give me a conflict scenario")
        Greetings & casual conversation
        You are not supposed to provide feedback it is the dury of other agents
    </General Agent>

"""

)


class Router(TypedDict):
        """Worker to route to next"""
        next: Literal["story_agent","conflict_agent","impromptu_agent","general_agent"]


class State(MessagesState):
    next: str


def supervisor_node(state:State) -> Command[Literal["story_agent","conflict_agent","impromptu_agent","general_agent"]]       :
    messages=[
         {"role":"system","content":system_prompt}
    ]   + state['messages']  
    response = llm.with_structured_output(Router).invoke(messages)
    goto =response['next']
    
    
    return Command(goto=goto,update={'next':goto})



def story_node(state: State) -> Command[Literal[END]]: # type: ignore
    result = story_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="story_agent")
            ]
        },
        goto=END,
    )    

def impromptu(state: State) -> Command[Literal[END]]: # type: ignore
    result = impromptu_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="impromptu_agent")
            ]
        },
        goto=END,
    )   

def conflict(state: State) -> Command[Literal[END]]: # type: ignore
    result = conflict_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="conflict_agent")
            ]
        },
        goto=END,
    ) 

def general(state:State)-> Command[Literal[END]]: # type: ignore
      # Extract the last user message
    result = general_agent.invoke(state) 
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="general_agent")
            ]
        },
        goto=END,
    )


builder = StateGraph(State)

builder.add_node("supervisor", supervisor_node)
builder.add_node("conflict_agent", conflict)
builder.add_node("impromptu_agent", impromptu)
builder.add_node("general_agent",general)
builder.add_node("story_agent", story_node)

builder.add_edge(START, "supervisor")




app= builder.compile()


