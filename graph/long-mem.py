import os, getpass
from dotenv import load_dotenv
from bs4.filter import SoupStrainer

load_dotenv()

open_ai_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = open_ai_key

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(
    model="moonshotai/kimi-k2:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

vector_store = Chroma(
    collection_name="long-term-graph",
    embedding_function=embeddings,
    persist_directory="long_term_db",
)

loader = WebBaseLoader(
    web_path=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    )
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

#print(all_splits[0])

_ = vector_store.add_documents(documents = all_splits)

# retrieval 

results = vector_store.similarity_search(
    "What is task decomposition in AI agents?", k=3
)

#print(results)

