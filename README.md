# Jupyter Notebook Samples with Tanzu Platform
This repository provides JupyterLab notebooks built with Python, leveraging LangChain and LangGraph. They demonstrate patterns for connecting to a variety of services—such as large language models, data services, and vector databases deployed on to Tanzu Platform, formerly know as Tanzu Application Services (TAS) or Pivotal Cloud Foundry (PCF), while incorporating service discovery and credential management.

## Why JupyterLab on Tanzu Platform?

### Collaborative Research Platform
- Data Scientists can prototype AI models and analyze results interactively
- ML Engineers can test model integrations and performance
- Application Developers can experiment with AI features before building production apps
- Platform Teams maintain governance and cost control across all usage
### Integrated Workflow Benefits
When JupyterLab is bound to multiple services, you get:
- Data Services connectivity with advanced caching and Retrieval Augmented Generation (RAG) with Tanzu GemFire or Tanzu Valkey, event streaming with Tanzu RabbitMQ, or simplied RAG usecases for data exploration and feature engineering
- Pre-approved LLM access for natural language processing and generation experiments
- Vector database capabilities (GemFire, Valkey, Postgres, or MySQL) for embedding storage and similarity search
- Automatic service discovery and credential management through Tanzu Platform
- Built-in observability for tracking resource usage and model performance


## Getting started
- git clone repository https://github.com/yannicklevederpvtl/cf-jupyterlab-uv
- Add Python Packages by editing pyproject.toml:
<pre>
langgraph-checkpoint-sqlite
tavily-python
langchain-mcp-adapters
matplotlib
unstructured
pydub
modal
ollama
</pre>

or use command in a JupyterLab Terminal

<pre> 
  uv pip add <package></package> 
</pre>

- Deploy JupyterLab for Cloud Foundry into your Tanzu Platform environment using the repository https://github.com/yannicklevederpvtl/cf-jupyterlab-uv
<pre>
  cf push -f manifest.yml
</pre>
- Open Jupyter Lab console and use git menu to clone the cf-jupyterlab-samples and start coding


## Running Notebooks locally
- Install uv with the official guide https://docs.astral.sh/uv/getting-started/installation/
- Clone the github repository
- project already has pyproject.toml file
<pre>
  uv sync
</pre>
- Launch Jupyter notebook with uv
<pre>
  uv run --with jupyter jupyter lab
</pre>
- Open the notebooks
- Navigate to langChainNotebooks
- start with `langchain_agent.ipynb file
- you may need to comment out following lines
  <pre>
    chat_service = env.get_service(name="gen-ai-qwen3-ultra")
    chat_credentials = chat_service.credentials
  </pre>
- Update model credentials with your credentials
  <pre>
    llm = ChatOpenAI(
    temperature=0.9,
    model=your_model_name,
    base_url=your_model_base,
    api_key=your_api_key,
    http_client=httpx_client
)
  </pre>
- Run notebook locally instead of only on Tanzu Platform
  





