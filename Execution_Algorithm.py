import xml.etree.ElementTree as ET
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from HelperMethods import clean_xml
from langchain import PromptTemplate
from langchain_core.runnables import RunnableLambda
from BFS_Tree_Planner_Prompt import replanner_prompt_template_xml
from langchain_openai import ChatOpenAI


def convert_tools(tools: List[Any]) -> str:
    """
    Convert a list of tools to a formatted string.

    Args:
        tools (List[Any]): A list of tool objects.

    Returns:
        str: A formatted string representation of the tools.
    """
    return "\n".join([f"{tool.name}: {tool.description}" for tool in tools])


class ExecutionAlgorithm:
    """
    A class to handle the execution and replanning of tasks using BFS and DFS approaches.
    """

    def __init__(self, list_of_tools: List[Any], replan_enable: bool = False, verbose: bool = False):
        """
        Initialize the ExecutionAlgorithm class.

        Args:
            list_of_tools (List[Any]): A list of tools available for task execution.
            replan_enable (bool): Flag to enable or disable replanning. Defaults to False.
            verbose (bool): Flag to enable or disable verbose output. Defaults to False.
        """
        self.verbose = verbose
        self.replan_enable = replan_enable

        self.list_of_tools_str = convert_tools(list_of_tools)
        self.tools: Dict[str, Any] = {tool.name: tool for tool in list_of_tools}
        self.model = ChatOpenAI(model="gpt-4o", temperature=0.1, max_tokens=4096)
        self.task_replanner_prompt = PromptTemplate.from_template(replanner_prompt_template_xml)
        self.tree_replanner_chain = (self.task_replanner_prompt
                                     | self.model
                                     | RunnableLambda(self.filter_clean_display_pass))

    def filter_clean_pass(self, modelResponse: Any) -> str:
        """
        Filter and clean the model response.

        Args:
            modelResponse (Any): The response from the model.

        Returns:
            str: The cleaned response.
        """
        clean = clean_xml(modelResponse.content)
        return clean

    def filter_clean_display_pass(self, modelResponse: Any) -> str:
        """
        Filter, clean, and optionally display the model response.

        Args:
            modelResponse (Any): The response from the model.

        Returns:
            str: The cleaned response.
        """
        try:
            clean = clean_xml(modelResponse.content)
        except:
            # replanner gives <NO_REPLAN> if no replan is needed
            # which is not a proper XML which might create error if not handled
            clean = modelResponse.content
        if self.verbose:
            print(f"Re-Planned Task Tree XML:\n{clean}")
        return clean

    def display_and_pass(self, ai_response: Any) -> str:
        """
        Display and pass the AI response.

        Args:
            ai_response (Any): The response from the AI model.

        Returns:
            str: The content of the AI response.
        """
        if self.verbose:
            print(f"Model Response:\n{ai_response.content}")
        return ai_response.content

    def display_prompt(self, prompt: str):
        """
        Display the given prompt if verbose is enabled.

        Args:
            prompt (str): The prompt to be displayed.
        """
        if self.verbose:
            print(f"Prompt:\n{prompt}")

    def replanner(self, task_tree_xml: str, tools_as_str: str) -> str:
        """
        Replan the task tree using the replaner model.

        Args:
            task_tree_xml (str): The current task tree in XML format.
            tools_as_str (str): A string representation of the tools available.

        Returns:
            str: The replaned task tree in XML format.
        """
        prompt = self.task_replanner_prompt.format(current_task_tree=task_tree_xml, tools=tools_as_str)
        #self.display_prompt(prompt)
        replan_response = self.tree_replanner_chain.invoke({"current_task_tree": task_tree_xml, "tools": tools_as_str})
        return replan_response

    def _execute_tool(self, action: str, action_input: str) -> str:
        """
        Execute a tool with the given action and input.

        Args:
            action (str): The action to be executed.
            action_input (str): The input for the action.

        Returns:
            str: The result of the tool execution.
        """
        tool = self.tools.get(action)
        if not tool:
            raise ValueError(f"Tool {action} not found.")
        print(f"Executing tool {action} with input: {action_input}")
        result = tool.run(action_input)
        #print(f"Tool {action} executed successfully. Result is {result}" )
        return result

    def _execute_task(self, task: ET.Element) -> ET.Element:
        """
        Execute a single task.

        Args:
            task (ET.Element): The task element to be executed.
        """
        print(f"Executing task:\n{ET.tostring(task, encoding='unicode')}") # Logging statement

        action = task.find('action').text
        action_input = task.find('action_input').text
        observation = task.find('observation')

        try:
            result = self._execute_tool(action, action_input)
            task.find('observation').text = result
        except Exception as e:
            task.find('observation').text = "Tool execution failed."
            print(f"Tool execution failed for action: {action} due to error: {e}")

        #print(f"Task result: \n{task.find('observation').text}")
        return task

    def process_task_bfs_parallel(self, xml_string: str) -> str:
        """
        Execute tasks in a breadth-first search (BFS) manner and optionally replan.

        Args:
            xml_string (str): The task tree in XML format.

        Returns:
            str: The final task tree in XML format after execution and replanning.
        """
        xml_string = clean_xml(xml_string)
        root = ET.fromstring(xml_string)
        queue = deque([root])

        while queue:
            node = queue.popleft()
            tasks = node.findall('.//task')

            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(self._execute_task, task): task for task in tasks if task.find('.//level_no').text.strip() != "0" and task.find('.//observation').text is None}
                print(f"Futures submitted: {futures}")  # Logging statement

                for future in as_completed(futures):
                    task = futures[future]
                    try:
                        future.result()
                        # Ensure the updated task is correctly placed back in the original tree
                        #node.replace(task, updated_task)
                    except Exception as e:
                        print(f"Task {task.find('.//task_no').text} failed due to {e}")

            for task in tasks:
                sub_tasks = task.find('.//sub_tasks')
                if sub_tasks is not None:
                    queue.extend(sub_tasks.findall('.//task'))

            if self.replan_enable:
                current_tree = ET.tostring(root, encoding='unicode')
                replan_xml = self.replanner(current_tree, self.list_of_tools_str)
                if replan_xml != "<NO_REPLAN>":
                    root = ET.fromstring(replan_xml)
                    queue = deque([root])

        response_xml = ET.tostring(root, encoding='unicode')
        return response_xml

    def process_task_dfs_parallel(self, xml_string: str) -> str:
        """
        Execute tasks in a depth-first search (DFS) manner and optionally replan.

        Args:
            xml_string (str): The task tree in XML format.

        Returns:
            str: The final task tree in XML format after execution and replanning.
        """
        xml_string = clean_xml(xml_string)
        root = ET.fromstring(xml_string)
        stack = [root]

        while stack:
            current_node = stack.pop()
            tasks = current_node.findall('.//task')

            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(self._execute_task, task): task for task in tasks if task.find('.//level_no').text.strip() != "0" and task.find('.//observation').text is None}
                print(f"Futures submitted: {futures}")  # Logging statement

                for future in as_completed(futures):
                    task = futures[future]
                    try:
                        future.result()
                        # Ensure the updated task is correctly placed back in the original tree
                        #current_node.replace(task, updated_task)
                    except Exception as e:
                        print(f"Task {task.find('.//task_no').text} failed due to {e}")

            for task in reversed(tasks):
                sub_tasks = task.find('.//sub_tasks')
                if sub_tasks is not None:
                    stack.extend(sub_tasks.findall('.//task'))

            if self.replan_enable:
                current_tree = ET.tostring(root, encoding='unicode')
                replan_xml = self.replanner(current_tree, self.list_of_tools_str)
                if replan_xml != "<NO_REPLAN>":
                    root = ET.fromstring(replan_xml)
                    stack = [root]

        response_xml = ET.tostring(root, encoding='unicode')
        return response_xml

    def process_task_bfs(self, xml_string: str) -> str:
        """
        Execute tasks in a breadth-first search (BFS) manner and optionally replan.

        Args:
            xml_string (str): The task tree in XML format.

        Returns:
            str: The final task tree in XML format after execution and replanning.
        """
        xml_string = clean_xml(xml_string)
        root = ET.fromstring(xml_string)
        queue = deque([root])

        while queue:
            node = queue.popleft()
            tasks = node.findall('.//task')

            for task in tasks:
                if task.find('.//level_no').text.strip() != "0" and task.find('.//observation').text is None:
                    try:
                        self._execute_task(task)
                    except Exception as e:
                        print(f"Task {task.find('.//task_no').text} failed due to {e}")

            for task in tasks:
                sub_tasks = task.find('.//sub_tasks')
                if sub_tasks is not None:
                    queue.extend(sub_tasks.findall('.//task'))

            if self.replan_enable:
                current_tree = ET.tostring(root, encoding='unicode')
                replan_xml = self.replanner(current_tree, self.list_of_tools_str)
                if replan_xml != "<NO_REPLAN>":
                    root = ET.fromstring(replan_xml)
                    queue = deque([root])

        response_xml = ET.tostring(root, encoding='unicode')
        return response_xml

    def process_task_dfs(self, xml_string: str) -> str:
        """
        Execute tasks in a depth-first search (DFS) manner and optionally replan.

        Args:
            xml_string (str): The task tree in XML format.

        Returns:
            str: The final task tree in XML format after execution and replanning.
        """
        xml_string = clean_xml(xml_string)
        root = ET.fromstring(xml_string)
        stack = [root]

        while stack:
            current_node = stack.pop()
            tasks = current_node.findall('.//task')

            for task in tasks:
                if task.find('.//level_no').text.strip() != "0" and task.find('.//observation').text is None:
                    try:
                        self._execute_task(task)
                    except Exception as e:
                        print(f"Task {task.find('.//task_no').text} failed due to {e}")

            for task in reversed(tasks):
                sub_tasks = task.find('.//sub_tasks')
                if sub_tasks is not None:
                    stack.extend(sub_tasks.findall('.//task'))

            if self.replan_enable:
                current_tree = ET.tostring(root, encoding='unicode')
                replan_xml = self.replanner(current_tree, self.list_of_tools_str)
                if replan_xml != "<NO_REPLAN>":
                    root = ET.fromstring(replan_xml)
                    stack = [root]

        response_xml = ET.tostring(root, encoding='unicode')
        return response_xml