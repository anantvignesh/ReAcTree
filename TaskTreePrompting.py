from langchain import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from BFS_Tree_Planner_Prompt import task_planner_prompt_template_xml, final_answer_prompt_template
from Execution_Algorithm import ExecutionAlgorithm
from HelperMethods import clean_xml
from langchain_openai import ChatOpenAI
import xml.etree.ElementTree as ET

def tool_name_and_description(tools):
    """
    Convert a list of tools to a formatted string.

    Args:
        tools (list): A list of tool objects.

    Returns:
        str: A formatted string representation of the tools.
    """
    return "\n".join([f"{tool.name}: {tool.description}" for tool in tools])

def tool_name(tools):
    """
    Convert a list of tools to a formatted string.

    Args:
        tools (list): A list of tool objects.

    Returns:
        str: A formatted string representation of the tools.
    """
    return ", ".join([tool.name for tool in tools])

class TaskTree:
    """
    A class to handle the planning, execution, and final answer composition using task trees.
    """

    def __init__(self, langchainTools, verbose=False, replan_enable=False):
        """
        Initialize the TaskTree class.

        Args:
            langchainTools (list): A list of LangChain tools available for task execution.
            verbose (bool): Flag to enable or disable verbose output. Defaults to False.
            replan_enable (bool): Flag to enable or disable replanning. Defaults to False.
        """
        self.verbose = verbose
        self.replan_enable = replan_enable
        self.model = ChatOpenAI(model="gpt-4o", temperature=0.1, max_tokens=4096)
        self.tools = langchainTools

        # Initialize the execution algorithm with the list of tools
        self.exec_algo = ExecutionAlgorithm(list_of_tools=self.tools, replan_enable=self.replan_enable, verbose=self.verbose)

        # Load prompts
        self.task_planner_prompt = PromptTemplate.from_template(task_planner_prompt_template_xml)
        self.final_answer_prompt = PromptTemplate.from_template(final_answer_prompt_template)

        # Define the chains for task planning and final answer composition
        self.tree_planner_chain = (self.task_planner_prompt
                                   | self.model
                                   | RunnableLambda(self.filter_clean_display_pass))

        self.final_answer_chain = ({"question": RunnableLambda(self.extract_original_question),
                                    "thought_process": RunnableLambda(self.extract_thoughts_and_observations)}
                                   | self.final_answer_prompt
                                   | RunnableLambda(self.display_prompt)  # optional display prompt going into the model
                                   | self.model
                                   | RunnableLambda(self.display_and_pass))

        # Define the BFS and DFS execution chains
        self.bfs_react_chain = (self.tree_planner_chain | RunnableLambda(self.exec_algo.process_task_bfs) | self.final_answer_chain)
        self.dfs_react_chain = (self.tree_planner_chain | RunnableLambda(self.exec_algo.process_task_dfs) | self.final_answer_chain)

    def filter_clean_pass(self, modelResponse):
        """
        Filter and clean the model response.

        Args:
            modelResponse (object): The response from the model.

        Returns:
            str: The cleaned response.
        """
        clean = clean_xml(modelResponse.content)
        return clean

    def filter_clean_display_pass(self, modelResponse):
        """
        Filter, clean, and optionally display the model response.

        Args:
            modelResponse (object): The response from the model.

        Returns:
            str: The cleaned response.
        """
        clean = clean_xml(modelResponse.content)
        if self.verbose:
            print(f"Task Tree XML:\n{clean}")
        return clean

    def display_and_pass(self, ai_response):
        """
        Display and pass the AI response.

        Args:
            ai_response (object): The response from the AI model.

        Returns:
            str: The content of the AI response.
        """
        if self.verbose:
            print(f"Model Response:\n{ai_response.content}")
        return ai_response.content

    def display_prompt(self, prompt):
        """
        Display the given prompt if verbose is enabled.

        Args:
            prompt (object): The prompt to be displayed.

        Returns:
            object: The prompt.
        """
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
        Parses an XML string to extract the original question.

        Args:
            xml_string (str): The XML string to be parsed.

        Returns:
            str: The original question.
        """
        root = ET.fromstring(xml_string)
        original_question = root.find(".//original_question").text
        return original_question

    def test_tree_planner(self, message):
        """
        Test the tree planner by invoking the tree planner chain.

        Args:
            message (str): The input question message.

        Returns:
            str: The response from the tree planner chain.
        """
        response = self.tree_planner_chain.invoke({"input_question": message,
                                                   "tools": tool_name_and_description(self.tools),
                                                   "tools_available": tool_name(self.tools)})
        return "```xml\n"+response+"\n```"

    def get_reply_bfs(self, message, verbose=False):
        """
        Get a reply using BFS execution.

        Args:
            message (str): The input question message.
            verbose (bool): Flag to enable or disable verbose output. Defaults to False.

        Returns:
            str: The response from the BFS execution chain.
        """
        self.verbose = verbose
        response = self.bfs_react_chain.invoke({"input_question": message,
                                                "tools": tool_name_and_description(self.tools),
                                                "tools_available": tool_name(self.tools)})
        return response

    def get_reply_dfs(self, message, verbose=False):
        """
        Get a reply using DFS execution.

        Args:
            message (str): The input question message.
            verbose (bool): Flag to enable or disable verbose output. Defaults to False.

        Returns:
            str: The response from the DFS execution chain.
        """
        self.verbose = verbose
        response = self.dfs_react_chain.invoke({"input_question": message,
                                                "tools": tool_name_and_description(self.tools),
                                                "tools_available": tool_name(self.tools)})
        return response