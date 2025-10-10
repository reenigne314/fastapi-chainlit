from IPython.display import Image, display
from typing_extensions import Literal

import sqlite3

from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
import os, getpass
from dotenv import load_dotenv

from PIL import Image
import io

# Load variables from .env file into the environment
load_dotenv()

class State(MessagesState):
    summary: str


def call_model(state: State):
    summary = state.get("summary", "")

    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]

    else:
        messages = state["messages"]

    response = llm.invoke(messages)
    return {"messages": response}


def summarize_conversation(state: State):
    summary = state.get("summary", "")

    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )

    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(messages)
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

    return {"summary": response.content, "messages": delete_messages}


def should_continue(state: State) -> Literal ["summarize_conversation", END]:
    messages = state["messages"]

    if len(messages) > 6:
        return "summarize_conversation"

    return END


# Create the ChatModel
# The rest of your code works as is, since the key is now in os.environ
llm = ChatOpenAI(
    model="moonshotai/kimi-k2:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)

def graph_builder():
    # Define a new graph
    workflow = StateGraph(State)
    workflow.add_node("conversation", call_model)
    workflow.add_node(summarize_conversation)

    # Set the entrypoint as conversation
    workflow.add_edge(START, "conversation")
    workflow.add_conditional_edges("conversation", should_continue)
    workflow.add_edge("summarize_conversation", END)

    return workflow
# Compile
workflow = graph_builder()
#graph = workflow.compile(checkpointer=memory)

# Get the PNG image data as bytes
#png_bytes = graph.get_graph().draw_mermaid_png()

# Open the image from the in-memory bytes and display it
#image = Image.open(io.BytesIO(png_bytes))
#image.show()