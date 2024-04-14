from langchain import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from BFS_Tree_Planner_Prompt import task_planner_prompt_template_xml, final_answer_prompt_template
from Execution_Algorithm import ExecutionAlgorithm
from HelperMethods import clean_xml
from langchain_openai import ChatOpenAI

import xml.etree.ElementTree as ET


# Logic for converting tools to string to go in prompt
def convert_tools(tools):
    return "\n".join([f"{tool.name}: {tool.description}" for tool in tools])

class TaskTree:
    def __init__(self, langchainTools, verbose=False):
        self.verbose = verbose
        self.model = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.1, max_tokens=4096)
        self.tools = langchainTools

        # Provide list of tools to the BFS react executor
        self.exec_algo = ExecutionAlgorithm(list_of_tools=self.tools)

        # load prompts
        self.task_planner_prompt = PromptTemplate.from_template(task_planner_prompt_template_xml)
        self.final_answer_prompt = PromptTemplate.from_template(final_answer_prompt_template)

        # tree planner chain
        self.tree_planner_chain = (self.task_planner_prompt
                                   | self.model
                                   | RunnableLambda(self.filter_clean_display_pass))

        # final answer composer chain
        self.final_answer_chain = ({"question": RunnableLambda(self.extract_original_question),
                                    "thought_process": RunnableLambda(self.extract_thoughts_and_observations)}
                                   | self.final_answer_prompt
                                   | RunnableLambda(self.display_prompt)  # optional display prompt going into the model
                                   | self.model
                                   | RunnableLambda(self.display_and_pass))

        self.bfs_react_chain = (self.tree_planner_chain | RunnableLambda(self.exec_algo.process_task_bfs) | self.final_answer_chain)
        self.dfs_react_chain = (self.tree_planner_chain | RunnableLambda(self.exec_algo.process_task_dfs) | self.final_answer_chain)

    def filter_clean_pass(self, modelResponse):
        # filter and clean
        clean = clean_xml(modelResponse.content)
        # pass
        return clean

    def filter_clean_display_pass(self, modelResponse):
        # filter and clean
        clean = clean_xml(modelResponse.content)
        # display
        if self.verbose:
            print(f"Task Tree XML:\n{clean}")
        # pass
        return clean

    def display_and_pass(self, ai_response):
        # display
        if self.verbose:
            print(f"Model Response:\n{ai_response.content}")
        # pass
        return ai_response.content

    def display_prompt(self, prompt):
        # display
        if self.verbose:
            print(prompt.text)
        return prompt

    def extract_thoughts_and_observations(self, xml_string):
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

    def extract_original_question(self, xml_string):
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

    def get_reply_bfs(self, message, verbose=False):
        self.verbose = verbose
        response = self.bfs_react_chain.invoke({"input_question": message, "tools": convert_tools(self.tools)})
        return response
    def get_reply_dfs(self, message, verbose=False):
        self.verbose = verbose
        response = self.dfs_react_chain.invoke({"input_question": message, "tools": convert_tools(self.tools)})
        return response