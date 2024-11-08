# agentic_system_graph.py

from typing import List
from typing_extensions import TypedDict
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from TaskTreePrompting import (
    State,
    langchain_tools,
    tools_dict,
    task_planning_node,
    task_execution_node,
    final_answer_node,
)

class AgenticSystemGraph:
    def __init__(self):
        # Build the LangGraph
        self.graph_builder = StateGraph(State)
        
        # Add nodes
        self.graph_builder.add_node('Task_Planning_Node', task_planning_node)
        self.graph_builder.add_node('Task_Execution_Node', task_execution_node)
        self.graph_builder.add_node('Final_Answer_Node', final_answer_node)
        
        # Define edges
        self.graph_builder.add_edge(START, 'Task_Planning_Node')
        self.graph_builder.add_edge('Task_Planning_Node', 'Task_Execution_Node')
        self.graph_builder.add_edge('Task_Execution_Node', 'Final_Answer_Node')
        self.graph_builder.add_edge('Final_Answer_Node', END)
        
        # Compile the graph
        self.graph = self.graph_builder.compile()
    
    def run(self, user_input: str) -> State:
        # Initialize the state
        initial_state = State(
            messages=[HumanMessage(content=user_input)],
            user_input=user_input,
            task_tree_json="",
            execution_result="",
            final_answer="",
            tools=tools_dict,
        )
        
        # Run the graph
        events = self.graph.stream(initial_state)
        final_state = None
        for event in events:
            state = event[next(iter(event))]
            last_message = state['messages'][-1].content
            print(last_message)  # Optional: Print the output at each step
            final_state = state  # Keep updating the final state
        
        return final_state  # Return the final state after execution