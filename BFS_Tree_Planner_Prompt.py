task_planner_prompt_template_xml = """
Task Tree Planning:

Carefully read and grasp the primary objective of the question.
Using only the available tools, start building your task tree. 
Fill in <thought>, <action>, and <action_input> relevant to the task completion.
Strictly keep the tags <observation> and <final_answer> in the tree for tree structure consistency but leave them blank.
Only add subtasks if essential, considering their action, action_input, and contribution towards the immediate and root task.
Document your task tree in the specified XML format, detailing all tasks and subtasks accordingly.

Use the following XML format to structure your task tree:

<task_tree>
  <task>
    <level_no>0</level_no>
    <task_no>0</task_no>
    <task_priority>1</task_priority>
    <parent_task_no>0</parent_task_no>
    <original_question>{input_question}</original_question>
    <thought>Your initial thought on how to approach and answer the original_question</thought>
    <is_leaf>is this a leaf node? yes/no</is_leaf>
    <sub_tasks>
      <task>
        <level_no>Subtask level number in the tree</level>
        <task_priority>task execution priority number at the current level</task_priority>
        <task_no>unique integer task number in the tree</task_no>
        <parent_task_no>Parent task numbers to signify what tasks from previous level preside this task in this tree level. eg. 1,2,..,N</parent_task_no>
        <thought>Your thought on this subtask</thought>
        <action>Action or tool for this subtask</action>
        <action_input>Input for this subtask's action or tool</action_input>
        <observation></observation>
        <is_leaf>is this a leaf node? yes/no</is_leaf>
        <sub_tasks>
          <!-- Nested subtasks if any necessary -->
        </sub_tasks>
      </task>
      <!-- Additional subtasks at this level any necessary -->
    </sub_tasks>
    <final_answer></final_answer>
  </task>
  <!-- No Additional tasks or subtasks at the root level-->
</task_tree>


Tools available to achieve the task:

{tools}

Question: {input_question}
Task Tree:
"""

replanner_prompt_template_xml = """
Replanning Task Tree:

Carefully review the existing task tree and the observations made so far.
Identify any points where the plan needs adjustment to better achieve the primary objective.
Using only the available tools, update the task tree as needed.
Fill in <thought>, <action>, and <action_input> relevant to the new or adjusted tasks.
Retain the tags <observation> and <final_answer> for tree structure consistency but leave them blank for any new tasks.
Only add new subtasks if essential, considering their action, action_input, and contribution towards the immediate and root task.
Document your updated task tree in the specified XML format.

REPLAN THE TASK TREE ONLY IF NECESSARY. DO NOT MAKE CHANGES FOR THE SAKE OF IT.
IF THE TASK TREE IS ALREADY OPTIMAL, DO NOT MAKE ANY CHANGES. JUST RETURN "<NO_REPLAN>".


Use the following XML format to structure your updated task tree:

<task_tree>
  <task>
    <level_no>0</level_no>
    <task_no>0</task_no>
    <task_priority>1</task_priority>
    <parent_task_no>0</parent_task_no>
    <original_question></original_question>
    <thought>Your initial thought on how to approach and answer the original_question</thought>
    <is_leaf>is this a leaf node? yes/no</is_leaf>
    <sub_tasks>
      <task>
        <level_no>Subtask level number in the tree</level>
        <task_priority>task execution priority number at the current level</task_priority>
        <task_no>unique integer task number in the tree</task_no>
        <parent_task_no>Parent task numbers to signify what tasks from previous level preside this task in this tree level. eg. 1,2,..,N</parent_task_no>
        <thought>Your thought on this subtask</thought>
        <action>Action or tool for this subtask</action>
        <action_input>Input for this subtask's action or tool</action_input>
        <observation></observation>
        <is_leaf>is this a leaf node? yes/no</is_leaf>
        <sub_tasks>
          <!-- Nested subtasks if any necessary -->
        </sub_tasks>
      </task>
      <!-- Additional subtasks at this level if any necessary -->
    </sub_tasks>
    <final_answer></final_answer>
  </task>
  <!-- No additional tasks or subtasks at the root level -->
</task_tree>

Current Task Tree:

{current_task_tree}

Tools available to achieve the task:

{tools}

Updated Task Tree:
"""

final_answer_prompt_template = """
Compose the final answer to the user's question from the thoughts and observations made from results of different tools.

Question: {question}

Thought Process:
{thought_process}

Final Answer:
"""