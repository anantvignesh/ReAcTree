task_planner_prompt_template_xml = """
Task Tree Planning:

Carefully read and grasp the primary objective of the question.
Using only the available tools, start building your task tree. 
Fill in <thought>, <action>, and <action_input> relevant to the task completion.
Leave <observation> and <final_answer> blank.
Only add subtasks if essential, considering their action, action_input, and contribution towards the immediate and root task.
Document your task tree in the specified XML format, detailing all tasks and subtasks accordingly.

Use the following XML format to structure your task tree:

<task_tree>
  <task>
    <level_no>0</level_no>
    <original_question>{input_question}</original_question>
    <thought>Your initial thought on how to approach and answer the original_question</thought>
    <is_leaf>is this a leaf node? yes/no</is_leaf>
    <sub_tasks>
      <task>
        <level_no>Subtask level number in the tree</level>
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

final_answer_prompt_template = """
Compose the final answer to the user's question from the thoughts and observations made from results of different tools.

Question: {question}

Thought Process:
{thought_process}

Final Answer:
"""