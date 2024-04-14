import os
# google
import vertexai
import google.cloud.bigquery as bq
# Langchain
from langchain_community.utilities import SQLDatabase
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_experimental.agents.agent_toolkits.python.base import create_python_agent
from langchain_experimental.tools import PythonREPLTool
from langchain.tools import tool, StructuredTool
from langchain_core.tools import ToolException
from langchain import PromptTemplate
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool
from langchain_google_vertexai import VertexAI

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.output_parsers import XMLOutputParser

from DBHelpers import BigQueryDBHelper
from BFS_Tree_Planner_Prompt import task_planner_prompt_template_xml, final_answer_prompt_template
from Execution_Algorithm import ExecutionAlgorithm
from HelperMethods import clean_xml, clean_sql

import xml.etree.ElementTree as ET

import re
import json

# Logic for converting tools to string to go in prompt
def convert_tools(tools):
    return "\n".join([f"{tool.name}: {tool.description}" for tool in tools])

def filter_clean_pass(modelResponse):
    # filter and clean
    clean = clean_xml(modelResponse.content)
    #pass
    return clean
    
def filter_clean_display_pass(modelResponse):
    # filter and clean
    clean = clean_xml(modelResponse.content)
    # display
    print(f"Task Tree XML:\n{clean}")
    #pass
    return clean

def display_and_pass(ai_response):
    # display
    print(f"Model Response:\n{ai_response.content}")
    #pass
    return ai_response.content

def extract_thoughts_and_observations(xml_string):
    """
    Parses an XML string to extract the initial thought or goal, and the thoughts
    and observations from leaf nodes marked with "yes".

    Args:
        xml_string (str): The XML string to be parsed.

    Returns:
        str: A formatted string containing the extracted information.
    """
    root = ET.fromstring(xml_string)
    initial_thought = root.find(".//thought").text
    leaf_thoughts_observations = []

    def process_node(node):
        for task in node.findall(".//task"):
            is_leaf = task.find("is_leaf").text
            if is_leaf.lower() == "yes":
                thought = task.find("thought").text
                observation = task.find("observation").text
                leaf_thoughts_observations.append((thought, observation))

    process_node(root)

    # Format the output
    formatted_output = f"Initial Thought: {initial_thought}\n\n"
    formatted_output += "Leaf Thoughts and Observations:\n"
    for i, (thought, observation) in enumerate(leaf_thoughts_observations, start=1):
        formatted_output += f"{i}. Thought: {thought}, Observation: {observation}\n"

    return formatted_output.strip()

def extract_original_question(xml_string):
    """
    Parses an XML string to extract the original_question.

    Args:
        xml_string (str): The XML string to be parsed.

    Returns:
        str: original question.
    """
    root = ET.fromstring(xml_string)
    original_question = root.find(".//original_question").text

    return original_question

def display_prompt(prompt):
    print(prompt)
    return prompt


class TaskTree:
    def __init__(self, langchainTools):

        self.tools = langchainTools

        # Provide list of tools to the BFS react executor
        exec_algo = ExecutionAlgorithm(list_of_tools=self.tools)

        # load prompts
        self.task_planner_prompt = PromptTemplate.from_template(task_planner_prompt_template_xml)
        self.final_answer_prompt = PromptTemplate.from_template(final_answer_prompt_template)

        # tree planner chain
        self.tree_planner_chain = (task_planner_prompt 
                              | model 
                              | RunnableLambda(filter_clean_pass))
                              #| RunnableLambda(filter_clean_display_pass))

        # final answer composer chain
        self.final_answer_chain = ({"question":RunnableLambda(extract_original_question), 
                               "thought_process":RunnableLambda(extract_thoughts_and_observations)} 
                              | final_answer_prompt 
                              | RunnableLambda(display_prompt) # optional display prompt going into the model
                              | model 
                              | RunnableLambda(display_and_pass))

        self.bfs_react_chain = (tree_planner_chain | RunnableLambda(exec_algo.process_task_bfs) | final_answer_chain)
        self.dfs_react_chain = (tree_planner_chain | RunnableLambda(exec_algo.process_task_dfs) | final_answer_chain)

    def get_reply_bfs(self, message, verbose=False):
        response = self.bfs_react_chain.invoke({"input_question": message, "tools":convert_tools(self.tools)})

    def get_reply_dfs(self, message, verbose=False):
        response = self.dfs_react_chain.invoke({"input_question": message, "tools":convert_tools(self.tools)})