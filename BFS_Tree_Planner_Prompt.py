task_planner_prompt_template_json = """
Task Tree Planning:

Carefully read and grasp the primary objective of the question.
Using only the available tools, start building your task tree.
Fill in "thought", "action", and "action_input" relevant to the task completion.
Strictly keep the keys "observation" and "final_answer" in the tree for tree structure consistency but leave them blank.
Only add subtasks if essential, considering their action, action_input, and contribution towards the immediate and root task.
Document your task tree in the specified JSON format, detailing all tasks and subtasks accordingly.

Use the following JSON format to structure your task tree:

{{
  "task_tree": {{
    "task": {{
      "prime_objective": "{prime_objective}",
      "level_no": 0,
      "task_no": 0,
      "task_priority": 1,
      "parent_task_no": 0,
      "original_question": "{input_question}",
      "tools_available": "{tools_available}",
      "thought": "Your initial thought on how to approach and answer the original_question",
      "is_leaf": "is this a leaf node? yes/no",
      "sub_tasks": [
        {{
          "level_no": "Subtask level number in the tree",
          "task_priority": "Task execution priority number at the current level",
          "task_no": "Unique integer task number in the tree",
          "parent_task_no": "Parent task number to signify which task from the previous level precedes this task in this tree level. e.g., 1,2,..,N",
          "thought": "Your thought on this subtask",
          "action": "Action or tool for this subtask",
          "action_input": "Input for this subtask's action or tool",
          "observation": "",
          "is_leaf": "is this a leaf node? yes/no",
          "sub_tasks": [
            // Nested subtasks if any necessary
          ]
        }}
        // Additional subtasks at this level if any necessary
      ],
      "final_answer": ""
    }}
  }}
}}

Tools available to achieve the task:

{tools}

Question: {input_question}
Task Tree:
"""

replanner_prompt_template_json = """
Replanning Task Tree:

Carefully review the existing task tree and the observations made so far.
Identify any points where the plan needs adjustment to better achieve the primary objective.
Using only the available tools, update the task tree as needed.
Fill in "thought", "action", and "action_input" relevant to the new or adjusted tasks.
Retain the keys "observation" and "final_answer" for tree structure consistency but leave them blank for any new tasks.
Only add new subtasks if essential, considering their action, action_input, and contribution towards the immediate and root task.
Document your updated task tree in the specified JSON format.

DO NOT GENERATE REASONS. YOU WILL EITHER GENERATE AN UPDATED TASK TREE JSON OR RETURN "<NO_REPLAN>".
REPLAN THE TASK TREE ONLY IF NECESSARY. DO NOT MAKE CHANGES FOR THE SAKE OF IT.
FOR TOOL EXECUTION ERROR, USE ONLY THE TOOLS AVAILABLE IN THE ORIGINAL TASK TREE TO REPLAN THE TASK TREE.
IF THE TASK TREE IS ALREADY OPTIMAL, DO NOT MAKE ANY CHANGES. JUST RETURN "<NO_REPLAN>".

Use the following JSON format to structure your updated task tree:

{{
  "task_tree": {{
    "task": {{
      "prime_objective": "",
      "level_no": 0,
      "task_no": 0,
      "task_priority": 1,
      "parent_task_no": 0,
      "original_question": "",
      "tools_available": "",
      "thought": "Your initial thought on how to approach and answer the original_question",
      "is_leaf": "is this a leaf node? yes/no",
      "sub_tasks": [
        {{
          "level_no": "Subtask level number in the tree",
          "task_priority": "Task execution priority number at the current level",
          "task_no": "Unique integer task number in the tree",
          "parent_task_no": "Parent task number to signify which task from the previous level precedes this task in this tree level. e.g., 1,2,..,N",
          "thought": "Your thought on this subtask",
          "action": "Action or tool for this subtask",
          "action_input": "Input for this subtask's action or tool",
          "observation": "",
          "is_leaf": "is this a leaf node? yes/no",
          "sub_tasks": [
            // Nested subtasks if any necessary
          ]
        }}
        // Additional subtasks at this level if any necessary
      ],
      "final_answer": ""
    }}
  }}
}}

Current Task Tree:

{current_task_tree}

Tools available to achieve the task:

{tools}

Updated Task Tree:
"""

final_answer_prompt_template_json = """
Compose the final answer to the user's question from the thoughts and observations made from results of different tools.

Question: {question}

Thought Process:
{thought_process}

Final Answer:
"""