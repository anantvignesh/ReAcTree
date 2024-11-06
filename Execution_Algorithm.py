import json
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from HelperMethods import clean_json
from langchain import PromptTemplate
from langchain_core.runnables import RunnableLambda
from BFS_Tree_Planner_Prompt import replanner_prompt_template_json
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
        self.model = ChatOpenAI(model="gpt-4", temperature=0.1, max_tokens=4096)
        self.task_replanner_prompt = PromptTemplate.from_template(replanner_prompt_template_json)
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
        clean = clean_json(modelResponse.content)
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
            clean = clean_json(modelResponse.content)
        except:
            # Replanner gives <NO_REPLAN> if no replan is needed
            # which is not a proper JSON, so we handle it
            clean = modelResponse.content
        if self.verbose:
            print(f"Re-Planned Task Tree JSON:\n{clean}")
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

    def replanner(self, task_tree_json: str, tools_as_str: str) -> str:
        """
        Replan the task tree using the replanner model.

        Args:
            task_tree_json (str): The current task tree in JSON format.
            tools_as_str (str): A string representation of the tools available.

        Returns:
            str: The replanned task tree in JSON format.
        """
        prompt = self.task_replanner_prompt.format(current_task_tree=task_tree_json, tools=tools_as_str)
        # self.display_prompt(prompt)
        replan_response = self.tree_replanner_chain.invoke({"current_task_tree": task_tree_json, "tools": tools_as_str})
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
        # print(f"Tool {action} executed successfully. Result is {result}")
        return result

    def _execute_task(self, task: dict) -> dict:
        """
        Execute a single task.

        Args:
            task (dict): The task dictionary to be executed.

        Returns:
            dict: The updated task dictionary.
        """
        print(f"Executing task:\n{json.dumps(task, indent=2)}")  # Logging statement

        action = task.get('action')
        action_input = task.get('action_input')
        observation = task.get('observation')

        try:
            result = self._execute_tool(action, action_input)
            task['observation'] = result
        except Exception as e:
            task['observation'] = "Tool execution failed."
            print(f"Tool execution failed for action: {action} due to error: {e}")

        # print(f"Task result: \n{task.get('observation')}")
        return task

    def process_task_bfs_parallel(self, json_string: str) -> str:
        """
        Execute tasks in a breadth-first search (BFS) manner and optionally replan.

        Args:
            json_string (str): The task tree in JSON format.

        Returns:
            str: The final task tree in JSON format after execution and replanning.
        """
        json_string = clean_json(json_string)
        root = json.loads(json_string)
        queue = deque([root['task_tree']['task']])

        while queue:
            level_size = len(queue)
            current_level_tasks = []

            # Collect tasks at current level
            for _ in range(level_size):
                task = queue.popleft()
                current_level_tasks.append(task)

                # Enqueue subtasks for next level
                if 'sub_tasks' in task and isinstance(task['sub_tasks'], list):
                    queue.extend(task['sub_tasks'])

            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(self._execute_task, task): task for task in current_level_tasks
                           if str(task.get('level_no')).strip() != "0" and not task.get('observation')}
                print(f"Futures submitted: {futures}")  # Logging statement

                for future in as_completed(futures):
                    task = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Task {task.get('task_no')} failed due to {e}")

            if self.replan_enable:
                current_tree = json.dumps(root)
                replan_json = self.replanner(current_tree, self.list_of_tools_str)
                if replan_json != "<NO_REPLAN>":
                    root = json.loads(replan_json)
                    queue = deque([root['task_tree']['task']])

        response_json = json.dumps(root)
        return response_json

    def process_task_dfs_parallel(self, json_string: str) -> str:
        """
        Execute tasks in a depth-first search (DFS) manner and optionally replan.

        Args:
            json_string (str): The task tree in JSON format.

        Returns:
            str: The final task tree in JSON format after execution and replanning.
        """
        json_string = clean_json(json_string)
        root = json.loads(json_string)
        stack = [root['task_tree']['task']]

        while stack:
            task = stack.pop()

            if str(task.get('level_no')).strip() != "0" and not task.get('observation'):
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(self._execute_task, task)
                    print(f"Future submitted: {future}")  # Logging statement

                    try:
                        future.result()
                    except Exception as e:
                        print(f"Task {task.get('task_no')} failed due to {e}")

            # Push subtasks onto the stack in reverse order to maintain order
            if 'sub_tasks' in task and isinstance(task['sub_tasks'], list):
                stack.extend(reversed(task['sub_tasks']))

            if self.replan_enable:
                current_tree = json.dumps(root)
                replan_json = self.replanner(current_tree, self.list_of_tools_str)
                if replan_json != "<NO_REPLAN>":
                    root = json.loads(replan_json)
                    stack = [root['task_tree']['task']]

        response_json = json.dumps(root)
        return response_json

    def process_task_bfs(self, json_string: str) -> str:
        """
        Execute tasks in a breadth-first search (BFS) manner without parallelism and optionally replan.

        Args:
            json_string (str): The task tree in JSON format.

        Returns:
            str: The final task tree in JSON format after execution and replanning.
        """
        json_string = clean_json(json_string)
        root = json.loads(json_string)
        queue = deque([root['task_tree']['task']])

        while queue:
            task = queue.popleft()

            if str(task.get('level_no')).strip() != "0" and not task.get('observation'):
                try:
                    self._execute_task(task)
                except Exception as e:
                    print(f"Task {task.get('task_no')} failed due to {e}")

            # Enqueue subtasks for next level
            if 'sub_tasks' in task and isinstance(task['sub_tasks'], list):
                queue.extend(task['sub_tasks'])

            if self.replan_enable:
                current_tree = json.dumps(root)
                replan_json = self.replanner(current_tree, self.list_of_tools_str)
                if replan_json != "<NO_REPLAN>":
                    root = json.loads(replan_json)
                    queue = deque([root['task_tree']['task']])

        response_json = json.dumps(root)
        return response_json

    def process_task_dfs(self, json_string: str) -> str:
        """
        Execute tasks in a depth-first search (DFS) manner without parallelism and optionally replan.

        Args:
            json_string (str): The task tree in JSON format.

        Returns:
            str: The final task tree in JSON format after execution and replanning.
        """
        json_string = clean_json(json_string)
        root = json.loads(json_string)
        stack = [root['task_tree']['task']]

        while stack:
            task = stack.pop()

            if str(task.get('level_no')).strip() != "0" and not task.get('observation'):
                try:
                    self._execute_task(task)
                except Exception as e:
                    print(f"Task {task.get('task_no')} failed due to {e}")

            # Push subtasks onto the stack in reverse order to maintain order
            if 'sub_tasks' in task and isinstance(task['sub_tasks'], list):
                stack.extend(reversed(task['sub_tasks']))

            if self.replan_enable:
                current_tree = json.dumps(root)
                replan_json = self.replanner(current_tree, self.list_of_tools_str)
                if replan_json != "<NO_REPLAN>":
                    root = json.loads(replan_json)
                    stack = [root['task_tree']['task']]

        response_json = json.dumps(root)
        return response_json