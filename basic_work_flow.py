import os
from dotenv import load_dotenv
import chainlit as cl

# Load environment variables from .env file
load_dotenv()

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display


class State(TypedDict):
    input: str
    user_feedback: str
    counter: int


def step_1(state):
    state["counter"] = 0
    print("---Step 1---")
    return state


def human_feedback(state):
    print("---human_feedback---")
    pass

@cl.step(type="tool")
def step_3(state):
    state["counter"] += 1
    print(f"---Step 3---{state['counter']}")
    return state

def step_4(state):
    print("---Step 4---")
    pass

def router(state):
    if state["counter"] > 2:
        print("END")
        return "end"
    else:
        print("CONT")
        return "continue"

class sample_workflow_bot:

    def __init__(self):
        self.builder = StateGraph(State)
        self.builder.add_node("step_1", step_1)
        self.builder.add_node("human_feedback", human_feedback)
        self.builder.add_node("step_3", step_3)
        self.builder.add_node("step_4", step_4)
        
        self.builder.add_edge(START, "step_1")
        self.builder.add_edge("step_1", "human_feedback")
        self.builder.add_edge("human_feedback", "step_3")
        self.builder.add_edge("step_3", "step_4")
        self.builder.add_conditional_edges("step_4", router, {"end": END, "continue":"human_feedback"})
        
        # Set up memory
        self.memory = MemorySaver()
        
        # Add
        self.graph = self.builder.compile(checkpointer=self.memory, interrupt_before=["human_feedback"])