# Configuration Guide

## Overview

This guide covers advanced configuration options for the PDF to AstraDB applications.

## Environment Variables

### Required Variables

#### AstraDB Configuration
```env
API_ENDPOINT=https://your-database-id-region.apps.astra.datastax.com
APPLICATION_TOKEN=AstraCS:xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**API_ENDPOINT**: Your AstraDB database API endpoint
- Format: `https://{database-id}-{region}.apps.astra.datastax.com`
- Find in: AstraDB Console → Database → Connect tab

**APPLICATION_TOKEN**: Authentication token for AstraDB
- Format: `AstraCS:...` (starts with AstraCS:)
- Permissions: Database Administrator role required
- Generate in: AstraDB Console → Database → Settings → Tokens

#### OpenAI Configuration
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**OPENAI_API_KEY**: Your OpenAI API key
- Format: `sk-...` (starts with sk-)
- Find in: OpenAI Platform → API Keys
- Required for: Embeddings and LLM responses

### Optional Variables

```env
# Collection name for vector store (default: langchain_docling)
COLLECTION_NAME=my_custom_collection

# OpenAI model for embeddings (default: text-embedding-ada-002)
EMBEDDING_MODEL=text-embedding-ada-002

# OpenAI model for chat (default: gpt-3.5-turbo-16k)
CHAT_MODEL=gpt-3.5-turbo-16k

# Temperature for LLM responses (default: 0)
LLM_TEMPERATURE=0

# Streamlit port (default: 8501)
STREAMLIT_PORT=8501
```

## Application Configuration

### Console Application

The console application (`app_console_docling.py`) can be configured by modifying these parameters:

#### Collection Name
```python
astra_db_store = AstraDBVectorStore(
    collection_name="langchain_docling",  # Change this
    embedding=OpenAIEmbeddings(),
    token=os.getenv("APPLICATION_TOKEN"),
    api_endpoint=os.getenv("API_ENDPOINT")
)
```

#### LLM Model
```python
llm = ChatOpenAI(
    model="gpt-3.5-turbo-16k",  # Change model
    streaming=False,
    temperature=0  # Adjust temperature (0-1)
)
```

#### Query Prompt
```python
prompt = """
Answer the question based only on the supplied context. If you don't know the answer, say "I don't know".
Context: {context}
Question: {question}
Your answer:
"""
```

### GUI Application

The GUI application (`app_gui_docling.py`) configuration:

#### Page Configuration
```python
st.set_page_config(
    page_title="PDF to AstraDB - Docling",
    page_icon="📄",
    layout="wide"  # or "centered"
)
```

#### Collection Name
```python
astra_db_store = AstraDBVectorStore(
    collection_name="langchain_docling_gui",  # Change this
    embedding=OpenAIEmbeddings(),
    token=os.getenv("APPLICATION_TOKEN"),
    api_endpoint=os.getenv("API_ENDPOINT")
)
```

## Docling Configuration

### Document Converter Options

```python
from docling.document_converter import DocumentConverter

# Basic configuration
converter = DocumentConverter()

# Advanced configuration (if needed)
converter = DocumentConverter(
    # Add custom options here based on Docling documentation
)
```

### Document Processing

Customize element filtering:

```python
# Skip specific element types
skip_elements = ['header', 'footer', 'page_number']

for element, level in doc.iterate_items():
    element_type = element.label if hasattr(element, 'label') else 'text'
    
    if element_type.lower() in skip_elements:
        continue
    
    # Process element
```

## AstraDB Configuration

### Vector Store Settings

```python
from langchain_astradb import AstraDBVectorStore
from langchain_openai import OpenAIEmbeddings

astra_db_store = AstraDBVectorStore(
    collection_name="your_collection",
    embedding=OpenAIEmbeddings(
        model="text-embedding-ada-002",
        # chunk_size=1000,  # Uncomment to customize
    ),
    token=os.getenv("APPLICATION_TOKEN"),
    api_endpoint=os.getenv("API_ENDPOINT"),
    # namespace="default",  # Uncomment to use specific namespace
)
```

### Search Configuration

```python
# Configure retriever
retriever = astra_db_store.as_retriever(
    search_type="similarity",  # or "mmr"
    search_kwargs={
        "k": 4,  # Number of documents to retrieve
        # "fetch_k": 20,  # For MMR
        # "lambda_mult": 0.5,  # For MMR
    }
)
```

## OpenAI Configuration

### Embeddings

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    # chunk_size=1000,
    # max_retries=3,
)
```

### Chat Model

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-3.5-turbo-16k",
    temperature=0,  # 0 = deterministic, 1 = creative
    streaming=False,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    # max_tokens=1000,
    # request_timeout=60,
)
```

## Streamlit Configuration

### Server Settings

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Launch Script Configuration

Edit `scripts/launch_gui.sh`:

```bash
# Change default port
PORT=${1:-8501}

# Modify Streamlit options
nohup streamlit run app_gui_docling.py \
    --server.port=$PORT \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.maxUploadSize=200 \  # Add this for larger files
    > "$LOG_FILE" 2>&1 &
```

## Performance Tuning

### Memory Management

```python
# Limit document chunk size
MAX_CHUNK_SIZE = 1000  # characters

if len(current_doc.page_content) > MAX_CHUNK_SIZE:
    # Split into smaller chunks
    pass
```

### Batch Processing

```python
# Process documents in batches
BATCH_SIZE = 10

for i in range(0, len(documents), BATCH_SIZE):
    batch = documents[i:i + BATCH_SIZE]
    astra_db_store.add_documents(batch)
```

### Caching

```python
# For Streamlit, use caching
@st.cache_resource
def get_vector_store():
    return AstraDBVectorStore(...)

@st.cache_data
def process_pdf(file_path):
    return process_pdf_with_docling(file_path)
```

## Logging Configuration

### Console Application

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/console_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### GUI Application

Streamlit logs are automatically saved by the launch script to `logs/streamlit_*.log`.

## Security Best Practices

### Environment Variables

1. **Never commit .env files**
   - Already in .gitignore
   - Use .env.example for templates

2. **Rotate credentials regularly**
   - Update API keys periodically
   - Regenerate tokens after exposure

3. **Use minimal permissions**
   - AstraDB: Use role-based access
   - OpenAI: Set usage limits

### API Rate Limiting

```python
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    response = chain.invoke(question)
    print(f"Total Tokens: {cb.total_tokens}")
    print(f"Total Cost: ${cb.total_cost}")
```

## Troubleshooting Configuration

### Verify Configuration

```python
# Test script
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    "API_ENDPOINT",
    "APPLICATION_TOKEN",
    "OPENAI_API_KEY"
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {'*' * 10}")
    else:
        print(f"❌ {var}: Missing")
```

### Test Connections

```python
# Test AstraDB
from astrapy import DataAPIClient

client = DataAPIClient()
database = client.get_database(
    os.getenv("API_ENDPOINT"),
    token=os.getenv("APPLICATION_TOKEN")
)
print("✅ AstraDB connection successful")

# Test OpenAI
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.embeddings.create(
    input="test",
    model="text-embedding-ada-002"
)
print("✅ OpenAI connection successful")
```

## Advanced Configuration

### Custom Document Metadata

```python
metadata = {
    'source': file_path,
    'element_type': element_type,
    'page_number': page_num,
    'timestamp': datetime.now().isoformat(),
    'processed_by': 'docling',
}
```

### Custom Prompt Templates

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that answers questions based on provided context."),
    ("human", "Context: {context}\n\nQuestion: {question}"),
])
```

### Multiple Collections

```python
# Use different collections for different document types
collections = {
    'research': 'research_papers',
    'technical': 'technical_docs',
    'general': 'general_docs',
}

collection_name = collections.get(doc_type, 'general_docs')
```

## Configuration Checklist

- [ ] Environment variables set correctly
- [ ] AstraDB connection tested
- [ ] OpenAI API key validated
- [ ] Collection names configured
- [ ] LLM models selected
- [ ] Streamlit settings customized
- [ ] Logging configured
- [ ] Security measures implemented
- [ ] Performance tuning applied
- [ ] Backup strategy defined

---

**For additional help, refer to the official documentation of each component.**