import os
os.environ["OPENAI_API_KEY"]="[Your openAI API key here]"

import time
import gradio as gr
from langchain.agents import load_tools
from TaskTreePrompting import TaskTree

from tempfile import TemporaryDirectory
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


# Tool Configs
# file management tools
toolkit = FileManagementToolkit(root_dir="./tmp")
file_management_tools = toolkit.get_tools()
# wikipedia tool
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())


tools = load_tools(["arxiv"]) + file_management_tools + [wikipedia]

# bot initialization
bot = TaskTree(langchainTools=tools)

def slow_echo(message, history):
    response = bot.get_reply_bfs(message, verbose=True)
    for i in range(len(response)):
        time.sleep(0.01)
        yield response[: i + 1]


demo = gr.ChatInterface(slow_echo).queue()
demo.launch()