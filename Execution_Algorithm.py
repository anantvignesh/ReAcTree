import xml.etree.ElementTree as ET
from collections import deque
from HelperMethods import clean_xml  # Assuming clean_xml is correctly imported

from langchain import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from BFS_Tree_Planner_Prompt import replanner_prompt_template_xml, final_answer_prompt_template
from HelperMethods import clean_xml
from langchain_openai import ChatOpenAI

# utils
def convert_tools(tools):
    return "\n".join([f"{tool.name}: {tool.description}" for tool in tools])

class ExecutionAlgorithm:
    
    def __init__(self, list_of_tools:list, replan_enable=False, verbose=False):
        self.verbose = verbose
        self.replan_enable = replan_enable
        # Directly store the list of Langchain tools
        self.list_of_tools_str = convert_tools(list_of_tools)
        self.tools = {tool.name: tool for tool in list_of_tools}
        self.model = ChatOpenAI(model="gpt-4o", temperature=0.1, max_tokens=4096)

        self.task_replanner_prompt = PromptTemplate.from_template(replanner_prompt_template_xml)
        self.tree_replanner_chain = (self.task_replanner_prompt
                                   | self.model
                                   | RunnableLambda(self.filter_clean_display_pass))

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
        
    def _execute_tool(self, action, action_input):
        # Find and execute the tool based on action
        tool = self.tools.get(action)
        if tool:
            # Assuming the tool can be executed with .execute(action_input)
            #print(f"tool: {tool} | tool_input: {action_input}")
            return tool.run(action_input)
        else:
            print(f"No tool found for action: {action}")
            return "Tool execution failed."

    def replanner(self, xml_string, tools_list_str):
        """
        Replans the task tree based on the observations made from the results of different tools.
        Args:
            xml_string: str: task tree in XML format.
            tools_list_str: str: list of tools available to achieve the task.
        Returns:
            str: updated task tree in XML format.
        """
        # Run the replanner chain
        response = self.tree_replanner_chain.invoke({"current_task_tree": xml_string, "tools": tools_list_str})
        return response
        
    def process_task_dfs(self, xml_string):
        xml_string = clean_xml(xml_string)
        root = ET.fromstring(xml_string)

        # logic for dfs execution
        def process_node(node):
            #print(f"Current Node: {ET.tostring(node, encoding='unicode')}")
            for task in node.findall('task'):
                level_no = task.find('level_no').text
                #print(f"level_no: {level_no}")
                # skip looking for action in root node
                if level_no.strip()!="0":
                    action = task.find('action').text
                    action_input = task.find('action_input').text
                    observation = task.find('observation')

                    try:
                        # print(f"tool: {action} | tool_input: {action_input}")
                        print(f"Executing task no {task.find('task_no').text} with action: {action}")
                        result = self._execute_tool(action, action_input)
                        observation.text = result
                    except Exception as e:
                        print(f"Tool execution failed for action: {action}\n due to error: {e}")
                        observation.text = "Tool execution failed."

                    # result = self._execute_tool(action, action_input)
                    # observation.text = result

                # process any subtask to the queue by traversing deeper recursively
                sub_tasks = task.find('sub_tasks')
                if sub_tasks is not None:
                    process_node(sub_tasks)

            if self.replan_enable:
                # replan the task tree
                replan_xml = self.replanner(ET.tostring(node, encoding='unicode'), convert_tools(self.tools))
                if replan_xml != "<NO_REPLAN>":
                    #replan_xml = clean_xml(replan_xml)
                    node = ET.fromstring(replan_xml)

            return node

        # start processing in dfs approach
        root = process_node(root)

        # Replan if required after dfs execution of one iteration of the task tree
        # if self.replan_enable:
        #     # replan the task tree
        #     replan_xml = self.replanner(ET.tostring(root, encoding='unicode'), convert_tools(self.tools))
        #     if replan_xml == "<NO_REPLAN>":
        #         response_xml = ET.tostring(root, encoding='unicode')
        #     else:
        #         response_xml = replan_xml
        # else:
        #     response_xml = ET.tostring(root, encoding='unicode')

        response_xml = ET.tostring(root, encoding='unicode')
        #print(response_xml)
        return response_xml
        
    def process_task_bfs(self, xml_string):
        xml_string = clean_xml(xml_string)
        #print(f"xml_string:\n{xml_string}")
        root = ET.fromstring(xml_string)
        queue = deque([root])

        #logic for bfs execution, starting execution in bfs approach
        while queue:
            node = queue.popleft()
            #print(f"Current Node: {ET.tostring(node, encoding='unicode')}")
            for task in node.findall('task'):
                level_no = task.find('level_no').text
                #print(f"level_no: {level_no}")
                # skip looking for action in root node
                if level_no.strip()!="0":
                    action = task.find('action').text
                    action_input = task.find('action_input').text
                    observation = task.find('observation')

                    try:
                        # print(f"tool: {action} | tool_input: {action_input}")
                        print(f"Executing task no {task.find('task_no').text} with action: {action}")
                        result = self._execute_tool(action, action_input)
                        observation.text = result
                    except Exception as e:
                        print(f"Tool execution failed for action: {action}\n due to error: {e}")
                        observation.text = "Tool execution failed."

                    # result = self._execute_tool(action, action_input)
                    # observation.text = result

                # add any subtask to the queue
                sub_tasks = task.find('sub_tasks')
                if sub_tasks is not None:
                    queue.append(sub_tasks)

            # Replan if required after bfs execution of one iteration of the task tree
            if self.replan_enable:
                # replan the task tree
                replan_xml = self.replanner(ET.tostring(root, encoding='unicode'), self.list_of_tools_str)

                if replan_xml != "<NO_REPLAN>":
                    root = ET.fromstring(replan_xml)
                    
        response_xml = ET.tostring(root, encoding='unicode')

        #print(f"Updated XML After Tool Executions:\n{response_xml}")
        return response_xml