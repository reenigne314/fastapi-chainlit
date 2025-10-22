from io import BytesIO
import sys
import os
from dotenv import load_dotenv

import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.types import ThreadDict

from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage

# --- START: Path Correction ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# --- END: Path Correction ---

from graph import graph

load_dotenv()

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> bool:
    return cl.User(identifier=username)

@cl.data_layer
def get_data_layer():
    """Set up the data layer for storing conversation history"""
    return SQLAlchemyDataLayer(conninfo=os.environ["DATABASE_URL"])

@cl.on_chat_start
async def main():
    # Get the unique ID for this specific chat session
    thread_id = cl.context.session.id
    
    # Store the thread_id in the user's session to access it in on_message
    cl.user_session.set("thread_id", thread_id)
    await cl.Message(content="Hello! I'm a memory-enabled bot. How can I help you?").send()
    
@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    pass

@cl.on_message
async def on_message(message: cl.Message):
    """Handle text messages and images"""
    thread_id = cl.user_session.get("thead_id")

    # Specify a thread
    config = {"configurable": {"thread_id": thread_id}}

    # Specify an input
    messages = HumanMessage(content=message.content)

    # Run
    messages = graph.invoke({"messages": [messages]},config)

    final_content = messages['messages'][-1].content
    
    await cl.Message(content=final_content).send()