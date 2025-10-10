from io import BytesIO
import sys
import os

# --- START: Path Correction ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# --- END: Path Correction ---

import chainlit as cl
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langchain.schema.runnable.config import RunnableConfig
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from graph import graph
from langgraph.checkpoint.sqlite import SqliteSaver

@cl.on_chat_start
async def main():
    #cl.user_session.set("thread_id", 1)
    await cl.Message(content="Hello! I'm a memory-enabled bot. How can I help you?").send()

@cl.on_message
async def on_message(message: cl.Message):
    """Handle text messages and images"""
    msg = cl.Message(content="")

    # Process any attached images
    content = message.content

    thread_id = cl.user_session.get("id")

    # Specify a thread
    config = {"configurable": {"thread_id": thread_id}}

    # Specify an input
    messages = [HumanMessage(content=content)]

    # Run
    messages = graph.invoke({"messages": messages},config)

    #print(messages)

    final_content = messages['messages'][-1].content
    
    await cl.Message(content=final_content).send()