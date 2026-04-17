"""
Console Application: PDF to AstraDB Vector Store using Docling
This application replaces Unstructured-io with Docling for PDF processing
"""

import os
from dotenv import load_dotenv
from pathlib import Path

from docling.document_converter import DocumentConverter
from langchain_astradb import AstraDBVectorStore
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables
load_dotenv()

def process_pdf_with_docling(file_path: str) -> list:
    """
    Process PDF file using Docling and return structured documents
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of Document objects
    """
    print(f"\n📄 Processing PDF with Docling: {file_path}")
    
    # Initialize Docling converter
    converter = DocumentConverter()
    
    # Convert the PDF
    result = converter.convert(file_path)
    
    # Extract documents from Docling result
    documents = []
    current_doc = None
    
    # Process the document structure
    doc = result.document
    
    # Iterate through document elements
    for element, level in doc.iterate_items():
        element_type = element.label if hasattr(element, 'label') else 'text'
        
        # Skip headers and footers
        if element_type.lower() in ['header', 'footer']:
            continue
            
        # Start new document on titles
        if element_type.lower() == 'title':
            if current_doc is not None:
                documents.append(current_doc)
            current_doc = None
            
        # Initialize document if needed
        if not current_doc:
            metadata = {
                'source': file_path,
                'element_type': element_type,
            }
            current_doc = Document(page_content="", metadata=metadata)
        
        # Add content to current document
        if hasattr(element, 'text'):
            current_doc.page_content += element.text + "\n"
        
        # For tables, append and start new document
        if element_type.lower() == 'table':
            if current_doc is not None:
                documents.append(current_doc)
            current_doc = None
    
    # Add last document if exists
    if current_doc is not None:
        documents.append(current_doc)
    
    print(f"✅ Extracted {len(documents)} document chunks from PDF")
    return documents


def create_vector_store():
    """Create and return AstraDB vector store"""
    print("\n🗄️  Connecting to AstraDB Vector Store...")
    
    astra_db_store = AstraDBVectorStore(
        collection_name="langchain_docling",
        embedding=OpenAIEmbeddings(),
        token=os.getenv("APPLICATION_TOKEN"),
        api_endpoint=os.getenv("API_ENDPOINT")
    )
    
    print("✅ Connected to AstraDB")
    return astra_db_store


def query_vector_store(astra_db_store, question: str) -> str:
    """
    Query the vector store with a question
    
    Args:
        astra_db_store: AstraDB vector store instance
        question: Question to ask
        
    Returns:
        Answer string
    """
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
    
    return chain.invoke(question)


def main():
    """Main console application"""
    print("=" * 80)
    print("PDF to AstraDB Vector Store - Console Application (Docling)")
    print("=" * 80)
    
    # Check for input PDF
    input_dir = Path("input")
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in 'input' folder")
        return
    
    # Use first PDF file found
    pdf_file = pdf_files[0]
    print(f"\n📁 Using PDF file: {pdf_file}")
    
    # Process PDF with Docling
    documents = process_pdf_with_docling(str(pdf_file))
    
    if not documents:
        print("❌ No documents extracted from PDF")
        return
    
    # Display sample content
    print(f"\n📝 Sample content from first document:")
    print("-" * 80)
    print(documents[0].page_content[:400])
    print("-" * 80)
    
    # Create vector store
    astra_db_store = create_vector_store()
    
    # Add documents to vector store
    print(f"\n💾 Adding {len(documents)} documents to vector store...")
    astra_db_store.add_documents(documents)
    print("✅ Documents added successfully")
    
    # Query examples
    questions = [
        "What does reducing the attention key size do?",
        "For the transformer to English constituency results, what was the 'WSJ 23 F1' value for 'Dyer et al. (2016) (5]'?",
        "When was George Washington born?"
    ]
    
    print("\n" + "=" * 80)
    print("QUERY RESULTS")
    print("=" * 80)
    
    for i, question in enumerate(questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        print("-" * 80)
        response = query_vector_store(astra_db_store, question)
        print(f"💡 Answer: {response}")
        print("-" * 80)
    
    print("\n✅ Console application completed successfully!")


if __name__ == "__main__":
    main()

# Made with Bob
