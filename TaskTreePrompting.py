# task_tree_planner.py

import json
from typing import List, Dict, Any
from typing_extensions import TypedDict
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import Tool
from HelperMethods import clean_json
from BFS_Tree_Planner_Prompt import task_planner_prompt_template_json, final_answer_prompt_template_json

# Initialize the language model
llm = ChatOpenAI(model="gpt-4", temperature=0.1, max_tokens=4096)

# Create prompt templates
task_planner_prompt = PromptTemplate.from_template(task_planner_prompt_template_json)
final_answer_prompt = PromptTemplate.from_template(final_answer_prompt_template_json)

# Define the conversation state
class State(TypedDict):
    messages: List[BaseMessage]
    user_input: str
    task_tree_json: str
    execution_result: str
    final_answer: str
    tools: Dict[str, Tool]
    # Additional variables as needed

# Initialize tools (import your tools here)
from UtilityTools import (
    calculator,
    web_search,
    unit_converter,
    translate_text,
    summarize_text,
    # Include other tools as needed
)

# Wrap utility functions into LangChain tools
langchain_tools = [
    Tool(
        name="calculator",
        func=calculator,
        description="Performs mathematical calculations."
    ),
    Tool(
        name="web_search",
        func=web_search,
        description="Performs a web search and returns summarized results."
    ),
    Tool(
        name="unit_converter",
        func=unit_converter,
        description="Converts units from one type to another."
    ),
    Tool(
        name="translate_text",
        func=translate_text,
        description="Translates text to the specified language."
    ),
    Tool(
        name="summarize_text",
        func=summarize_text,
        description="Summarizes the given text."
    ),
    # Add more tools as needed
]

# Create a dictionary of tools for easy access
tools_dict = {tool.name: tool for tool in langchain_tools}

# Helper functions
def tool_name_and_description(tools):
    return "\n".join([f"{tool.name}: {tool.description}" for tool in tools.values()])

def tool_name(tools):
    return ", ".join([tool.name for tool in tools.values()])

def execute_task_tree(task_tree: dict, tools: Dict[str, Tool]) -> dict:
    """
    Executes the task tree using the provided tools.
    """
    def execute_task(task: dict):
        # If the task is a leaf node
        if task.get('is_leaf', '').lower() == 'yes':
            action = task.get('action')
            action_input = task.get('action_input')
            tool = tools.get(action)
            if tool:
                try:
                    print(f"Executing tool {action} with input: {action_input}")
                    result = tool.run(action_input)
                    task['observation'] = result
                    print(f"Result: {result}")
                except Exception as e:
                    task['observation'] = f"Error executing {action}: {e}"
                    print(f"Error executing {action}: {e}")
            else:
                task['observation'] = f"Tool {action} not found."
                print(f"Tool {action} not found.")
        # Recursively execute subtasks
        for sub_task in task.get('sub_tasks', []):
            execute_task(sub_task)

    execute_task(task_tree['task_tree']['task'])
    return task_tree

def extract_thoughts_and_observations(execution_result: str) -> str:
    """
    Extracts thoughts and observations from the execution result.
    """
    execution_data = json.loads(execution_result)
    thoughts = []

    def collect_thoughts(task: dict):
        thought = task.get('thought', '')
        observation = task.get('observation', '')
        if observation:
            thoughts.append(f"Thought: {thought}\nObservation: {observation}\n")
        for sub_task in task.get('sub_tasks', []):
            collect_thoughts(sub_task)

    collect_thoughts(execution_data['task_tree']['task'])
    return "\n".join(thoughts)

# Node functions

def task_planning_node(state: State) -> State:
    """
    Task Planning Node: Generates the task tree based on the user's input.
    """
    # Format the prompt
    prompt = task_planner_prompt.format(
        input_question=state['user_input'],
        tools=tool_name_and_description(state['tools']),
        tools_available=tool_name(state['tools'])
    )
    # Invoke the model
    response = llm(prompt)
    # Clean the response
    task_tree_json = clean_json(response.content)
    # Update the state
    state['task_tree_json'] = task_tree_json
    # Append to messages
    state['messages'].append(AIMessage(content=task_tree_json))
    return state

def task_execution_node(state: State) -> State:
    """
    Task Execution Node: Executes the tasks in the task tree.
    """
    # Parse the task tree
    task_tree = json.loads(state['task_tree_json'])
    # Execute the tasks
    execution_result = execute_task_tree(task_tree, state['tools'])
    # Update the state
    state['execution_result'] = json.dumps(execution_result)
    # Append to messages
    state['messages'].append(AIMessage(content=state['execution_result']))
    return state

def final_answer_node(state: State) -> State:
    """
    Final Answer Node: Composes the final answer based on the execution results.
    """
    # Extract the thought process and question from the execution result
    thought_process = extract_thoughts_and_observations(state['execution_result'])
    question = state['user_input']
    # Format the prompt
    prompt = final_answer_prompt.format(
        question=question,
        thought_process=thought_process
    )
    # Invoke the model
    response = llm(prompt)
    # Update the state
    state['final_answer'] = response.content.strip()
    # Append to messages
    state['messages'].append(AIMessage(content=state['final_answer']))
    return state