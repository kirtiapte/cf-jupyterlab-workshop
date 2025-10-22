from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_postgres.vectorstores import PGVector
import requests
import os
import requests
import json
import httpx
from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.agents import tool
from langchain.agents import initialize_agent, AgentType, load_tools
from langchain_core.tools import Tool
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from datetime import date
import warnings
import ssl
from langchain_community.embeddings import OllamaEmbeddings
from openai import OpenAI
from langchain.chains import RetrievalQA
import gradio as gr
import re
from cfenv import AppEnv
import sys, os
from tanzu_utils import CFGenAIService
# -----------------------------
# Embedding setup
# -----------------------------
# -----------------------------
# Load services from env
# -----------------------------
env = AppEnv()

# -----------------------------
# Embedding service details
# -----------------------------
embedding_service = CFGenAIService("tanzu-nomic-embed-text")

# List available models
embedding_models = embedding_service.list_models()
for m in embedding_models:
    print(f"- {m['name']} (capabilities: {', '.join(m['capabilities'])})")


API_BASE = embedding_service.api_base + "/openai/v1"
API_KEY = embedding_service.api_key
MODEL_NAME = embedding_models[0]["name"]



def embed_text(text: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,   # make sure MODEL_NAME is a str, not a tuple
        "input": text
    }

    print("HEADERS:", headers)
    print("PAYLOAD:", payload)

    resp = requests.post(
        f"{API_BASE}/embeddings",
        headers=headers,
        json=payload,
        verify=False
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]

class CustomEmbeddings:
    def embed_documents(self, texts): return [embed_text(t) for t in texts]
    def embed_query(self, text): return embed_text(text)

embedding = CustomEmbeddings()

# -----------------------------
# Vectorstore setup
# -----------------------------
# -----------------------------
# Database connection
# -----------------------------
db_service = env.get_service(name="vector-db")
db_credentials = db_service.credentials
DB_URI = db_credentials["uri"]

vectorstore = PGVector(
    embeddings=embedding,
    connection=DB_URI,
    collection_name="maintenance_and_taxonomy",
    use_jsonb=True,
    create_extension=False,   # already created
)
# -----------------------------
# RAG setup
# -----------------------------
# Get bound service "gen-ai-qwen3-ultra"
chat_service = CFGenAIService("tanzu-gpt-oss-120b")

# List available models
chat_models = chat_service.list_models()
for m in chat_models:
    print(f"- {m['name']} (capabilities: {', '.join(m['capabilities'])})")

# construct chat_credentials
chat_credentials = {
    "api_base": chat_service.api_base + "/openai/v1",
    "api_key": chat_service.api_key,
    "model_name": chat_models[0]["name"]
}

# Optional: configure custom http client
httpx_client = httpx.Client(verify=False)

# Initialize LLM with credentials from cfenv
llm = ChatOpenAI(
    temperature=0.9,
    model=chat_credentials["model_name"],
    base_url=chat_credentials["api_base"],
    api_key=chat_credentials["api_key"],
    http_client=httpx_client
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k":3})
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)


# -----------------------------
# Gradio chatbot function
# -----------------------------
def sanitize_answer(answer):
    # Convert sets to lists
    if isinstance(answer, set):
        answer = list(answer)
    # Convert anything else not string/dict/list to string
    if not isinstance(answer, (str, dict, list)):
        answer = str(answer)
    # Remove <think> tags if present
    if isinstance(answer, str):
        answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()
    return answer

def predict(message, history):
    # Run RetrievalQA
    output = qa.invoke({"query": message})  # dict: {"result", "source_documents"}
    answer = sanitize_answer(output["result"])
    return answer
    
demo = gr.ChatInterface(
    fn=predict,
    title="🛠 Aircraft Maintenance Chatbot",
    description="Ask questions about maintenance records or aircraft taxonomy."
)


demo.launch(
    share=True,
    server_name="0.0.0.0",
    server_port=7860,
    show_error=True,
    quiet=False
)
