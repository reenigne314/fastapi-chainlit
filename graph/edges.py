from IPython.display import Image, display
from typing_extensions import Literal

from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools.retriever import create_retriever_tool
from langgraph.prebuilt import ToolNode, tools_condition

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from bs4.filter import SoupStrainer

from PIL import Image
import io

# Load variables from .env file into the environment
load_dotenv()

# Create the ChatModel
# The rest of your code works as is, since the key is now in os.environ
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

llm = ChatOpenAI(
    model="qwen/qwen3-vl-235b-a22b-instruct",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)

vector_store = Chroma(
    collection_name="long-term-graph",
    embedding_function=embeddings,
    persist_directory="long_term_db",
)

#create retriver tool
retriever = vector_store.as_retriever(search_kwargs={"k":3})
retriever_tool = create_retriever_tool(
    retriever=retriever,
    name="LongTermMemoryRetriever",
    description="Useful for retrieving information from long term memory to answer questions about previously ingested documents.",
)

llm_with_tool = llm.bind_tools([retriever_tool])

class State(MessagesState):
    summary: str


def call_model(state: State):
    summary = state.get("summary", "")

    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]

    else:
        messages = state["messages"]

    response = llm_with_tool.invoke(messages)
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


def web_scrape(web_path: str):
    loader = WebBaseLoader(
        web_path=(web_path),
        bs_kwargs=dict(
            parse_only=SoupStrainer(
                class_=("post-content", "post-title", "post-header")
            )
        )
    )
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    return all_splits

def add_files_vector_store(splits):
    _ = vector_store.add_documents(documents = splits)
    return _

def graph_builder():
    # Define a new graph
    workflow = StateGraph(State)
    workflow.add_node("conversation", call_model)
    workflow.add_node("tools", ToolNode([retriever_tool]))
    workflow.add_node(summarize_conversation)

    # Set the entrypoint as conversation
    workflow.add_edge(START, "conversation")
    workflow.add_conditional_edges("conversation", tools_condition)
    workflow.add_edge("tools", "conversation")
    workflow.add_conditional_edges("conversation", should_continue)
    workflow.add_edge("summarize_conversation", END)

    return workflow
'''# Compile
workflow = graph_builder()
# Define the connection to the existing Sqlite database
db_path = "example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)

memory = SqliteSaver(conn)
graph = workflow.compile(checkpointer=memory)

# Specify a thread
config = {"configurable": {"thread_id": 1}}

# Specify an input
messages = [HumanMessage(content="Hello!"),]

# Run
messages = graph.invoke({"messages": messages},config)'''

# Get the PNG image data as bytes
#png_bytes = graph.get_graph().draw_mermaid_png()

#Open the image from the in-memory bytes and display it
#image = Image.open(io.BytesIO(png_bytes))
#image.show()