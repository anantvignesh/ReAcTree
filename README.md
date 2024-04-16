# ReAcTree

ReAcTree revolutionizes React prompting by adopting a structured task tree approach, offering a novel way to manage and execute complex tasks in a systematic and efficient manner. Designed for seamless integration with existing Langchain tools, this project utilizes an AI model to generate task trees in an XML format, providing a strategic, look-ahead planning mechanism to guide the execution of tasks.

## Installation

ReAcTree requires Python 3.11 or higher. Installation is straightforward via pip:

```bash
pip install reactree
```

Ensure that your environment meets the required Python version to avoid any compatibility issues.

## Usage

ReAcTree is designed to be user-friendly and easily integrable into existing projects with Langchain tools. To utilize ReAcTree, import and initialize the `TaskTree` class with your choice of Langchain tools. The system will automatically handle the task execution using either Breadth-First Search (BFS) or Depth-First Search (DFS) algorithms, based on the structure of the task tree.

### Example

Here's a simple example of how to use ReAcTree:

```python
from TaskTreePrompting import TaskTree

# Initialize the bot with Langchain tools
tools = # (Specify your Langchain tools configuration here)
bot = TaskTree(langchainTools=tools)
```

This setup will enable the AI to create a Task Tree, execute tasks in a specified order, and compile the results efficiently.

## Features

**Key features of ReAcTree include:**

- **Open Source**: Fully open-source, allowing for community contributions and enhancements.
- **Integrated Task Execution**: Incorporates a sophisticated 'LLM Compiler' that executes tasks based on the generated XML task tree.
- **Efficient Result Compilation**: Results of task executions are embedded within the XML under the `<observation>` tags, with the system extracting observations from leaf nodes only to optimize performance and accuracy.
- **Compatibility with Langchain Tools**: Designed to be compatible with existing Langchain tools, facilitating easy integration and widespread adoption.

## Disclaimer

ReAcTree is under active development. Features and documentation may evolve over time. We encourage you to star and watch this repository for updates on exciting new features and improvements.
