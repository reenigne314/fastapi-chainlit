import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from graph.shortmem import graph_builder

# Define the connection to the existing Sqlite database
db_path = "example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)

memory = SqliteSaver(conn)
workflow = graph_builder()
graph = workflow.compile(checkpointer=memory)