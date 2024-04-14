import xml.etree.ElementTree as ET
from collections import deque
from HelperMethods import clean_xml  # Assuming clean_xml is correctly imported

class ExecutionAlgorithm:
    
    def __init__(self, list_of_tools=[]):
        # Directly store the list of Langchain tools
        self.tools = {tool.name: tool for tool in list_of_tools}
        
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
                    #print(f"tool: {action} | tool_input: {action_input}")
                    result = self._execute_tool(action, action_input)
                    observation.text = result

                # process any subtask to the queue by traversing deeper recursively
                sub_tasks = task.find('sub_tasks')
                if sub_tasks is not None:
                    process_node(sub_tasks)

        # start processing in dfs approach
        process_node(root)

        response_xml = ET.tostring(root, encoding='unicode')
        print(response_xml)
        return response_xml
        
    def process_task_bfs(self, xml_string):
        xml_string = clean_xml(xml_string)
        print(f"xml_string:\n{xml_string}")
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
                    #print(f"tool: {action} | tool_input: {action_input}")
                    result = self._execute_tool(action, action_input)
                    observation.text = result

                # add any subtask to the queue
                sub_tasks = task.find('sub_tasks')
                if sub_tasks is not None:
                    queue.append(sub_tasks)
                    
        response_xml = ET.tostring(root, encoding='unicode')
        print(f"Updated XML After Tool Executions:\n{response_xml}")
        return response_xml