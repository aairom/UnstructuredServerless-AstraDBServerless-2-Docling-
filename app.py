
# https://docs.datastax.com/en/astra-db-serverless/api-reference/dataapiclient.html
# https://docs.datastax.com/en/astra-db-serverless/integrations/unstructured-io.html

# Import dependencies and load environment variables:
import os
import requests

from dotenv import load_dotenv
from langchain_astradb import AstraDBVectorStore
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain_community.document_loaders import (
    unstructured,
    UnstructuredAPIFileLoader,
)

from langchain_openai import (
    ChatOpenAI,
    OpenAIEmbeddings,
)

load_dotenv()

# download a PDF to parse
url = "https://raw.githubusercontent.com/datastax/ragstack-ai/48bc55e7dc4de6a8b79fcebcedd242dc1254dd63/examples/notebooks/resources/attention_pages_9_10.pdf"
file_path = "./attention_pages_9_10.pdf"

response = requests.get(url)
if response.status_code == 200:
    with open(file_path, "wb") as file:
        file.write(response.content)
    print("Download complete.")
else:
    print("Error downloading the file.")

# Advanced Parsing
elements = unstructured.get_elements_from_api(
    file_path="./attention_pages_9_10.pdf",
    api_key=os.getenv("UNSTRUCTURED_API_KEY"),
    server_url=os.getenv("UNSTRUCTURED_API_URL"),
    strategy="hi_res", # default "auto"
    pdf_infer_table_structure=True,
)

print(len(elements))
tables = [el for el in elements if el.category == "Table"]
print(tables[1].metadata.text_as_html)    


astra_db_store = AstraDBVectorStore(
    collection_name="langchain_unstructured",
    embedding=OpenAIEmbeddings(),
    token=os.getenv("APPLICATION_TOKEN"),
    api_endpoint=os.getenv("API_ENDPOINT")
)

# Create a Serverless (vector) store instance:
astra_db_store = AstraDBVectorStore(
    collection_name="langchain_unstructured",
    embedding=OpenAIEmbeddings(),
    token=os.getenv("APPLICATION_TOKEN"),
    api_endpoint=os.getenv("API_ENDPOINT")
)

# Use the following code to create LangChain documents. This code chunks the text after Table elements and before Title elements, 
# uses the HTML output format for table data, and then inserts the documents into the Astra DB vector store instance.
documents = []
current_doc = None

for el in elements:
    if el.category in ["Header", "Footer"]:
        continue # skip these
    if el.category == "Title":
        if current_doc is not None:
            documents.append(current_doc)
        current_doc = None
    if not current_doc:
        current_doc = Document(page_content="", metadata=el.metadata.to_dict())
    current_doc.page_content += el.metadata.text_as_html if el.category == "Table" else el.text
    if el.category == "Table":
        if current_doc is not None:
            documents.append(current_doc)
        current_doc = None

astra_db_store.add_documents(documents)

# Build a RAG pipeline using the populated vector store:
prompt = """
Answer the question based only on the supplied context. If you don't know the answer, say "I don't know".
Context: {context}
Question: {question}
Your answer:
"""

llm = ChatOpenAI(model="gpt-3.5-turbo-16k", streaming=False, temperature=0)

chain = (
    {"context": astra_db_store.as_retriever(), "question": RunnablePassthrough()}
    | PromptTemplate.from_template(prompt)
    | llm
    | StrOutputParser()
)

# Ask a question that the model can answer from the text in the parsed document:
response_1 = chain.invoke("What does reducing the attention key size do?")
print("\n***********New Unstructured Basic Query Engine***********")
print(response_1)

# Ask a question that the model can answer from the table data in the parsed document:
response_2 = chain.invoke("For the transformer to English constituency results, what was the 'WSJ 23 F1' value for 'Dyer et al. (2016) [8]'?")
print("\n***********New Unstructured Basic Query Engine***********")
print(response_2)

# Ask a question with an expected lack of context. This can be any query that has no relationship to the data in the parsed document.
response_3 = chain.invoke("When was George Washington born?")
print("\n***********New Unstructured Basic Query Engine***********")
print(response_3)

