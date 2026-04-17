"""
GUI Application: PDF to AstraDB Vector Store using Docling
Streamlit-based interface for PDF processing and querying
"""

import os
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

from docling.document_converter import DocumentConverter
from langchain_astradb import AstraDBVectorStore
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PDF to AstraDB - Docling",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False
if 'processing_log' not in st.session_state:
    st.session_state.processing_log = []


def log_message(message: str):
    """Add message to processing log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.processing_log.append(f"[{timestamp}] {message}")


def process_pdf_with_docling(file_path: str) -> list:
    """
    Process PDF file using Docling and return structured documents
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of Document objects
    """
    log_message(f"📄 Processing PDF with Docling: {file_path}")
    
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
    
    log_message(f"✅ Extracted {len(documents)} document chunks from PDF")
    return documents


def create_vector_store():
    """Create and return AstraDB vector store"""
    log_message("🗄️  Connecting to AstraDB Vector Store...")
    
    astra_db_store = AstraDBVectorStore(
        collection_name="langchain_docling_gui",
        embedding=OpenAIEmbeddings(),
        token=os.getenv("APPLICATION_TOKEN"),
        api_endpoint=os.getenv("API_ENDPOINT")
    )
    
    log_message("✅ Connected to AstraDB")
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
    """Main Streamlit application"""
    
    # Header
    st.title("📄 PDF to AstraDB Vector Store")
    st.subheader("Powered by Docling & Streamlit")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check environment variables
        api_endpoint = os.getenv("API_ENDPOINT")
        app_token = os.getenv("APPLICATION_TOKEN")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if api_endpoint and app_token and openai_key:
            st.success("✅ Environment variables loaded")
        else:
            st.error("❌ Missing environment variables")
            st.stop()
        
        st.divider()
        
        # File selection
        st.header("📁 PDF Selection")
        input_dir = Path("input")
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if not pdf_files:
            st.error("❌ No PDF files found in 'input' folder")
            st.stop()
        
        selected_pdf = st.selectbox(
            "Select PDF file:",
            options=[f.name for f in pdf_files],
            index=0
        )
        
        pdf_path = input_dir / selected_pdf
        
        st.divider()
        
        # Process button
        if st.button("🚀 Process PDF", type="primary", use_container_width=True):
            st.session_state.processing_log = []
            
            with st.spinner("Processing PDF..."):
                try:
                    # Process PDF
                    documents = process_pdf_with_docling(str(pdf_path))
                    
                    if not documents:
                        st.error("❌ No documents extracted from PDF")
                        st.stop()
                    
                    # Create vector store
                    st.session_state.vector_store = create_vector_store()
                    
                    # Add documents
                    log_message(f"💾 Adding {len(documents)} documents to vector store...")
                    st.session_state.vector_store.add_documents(documents)
                    log_message("✅ Documents added successfully")
                    
                    st.session_state.documents_loaded = True
                    st.success("✅ PDF processed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    log_message(f"❌ Error: {str(e)}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Query Interface")
        
        if st.session_state.documents_loaded:
            # Query input
            question = st.text_input(
                "Enter your question:",
                placeholder="What does reducing the attention key size do?"
            )
            
            if st.button("🔍 Search", type="primary"):
                if question:
                    with st.spinner("Searching..."):
                        try:
                            response = query_vector_store(
                                st.session_state.vector_store,
                                question
                            )
                            
                            st.subheader("💡 Answer:")
                            st.info(response)
                            
                            # Save to output
                            output_dir = Path("output")
                            output_dir.mkdir(exist_ok=True)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            output_file = output_dir / f"query_result_{timestamp}.txt"
                            
                            with open(output_file, "w") as f:
                                f.write(f"Question: {question}\n\n")
                                f.write(f"Answer: {response}\n")
                            
                            st.success(f"✅ Result saved to: {output_file}")
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a question")
            
            # Example questions
            st.divider()
            st.subheader("📝 Example Questions")
            
            example_questions = [
                "What does reducing the attention key size do?",
                "For the transformer to English constituency results, what was the 'WSJ 23 F1' value for 'Dyer et al. (2016) (5]'?",
                "When was George Washington born?"
            ]
            
            for i, eq in enumerate(example_questions, 1):
                if st.button(f"Example {i}: {eq}", key=f"example_{i}"):
                    st.session_state.example_question = eq
                    st.rerun()
            
            # Use example question if set
            if hasattr(st.session_state, 'example_question'):
                question = st.session_state.example_question
                delattr(st.session_state, 'example_question')
        else:
            st.info("👈 Please process a PDF file first using the sidebar")
    
    with col2:
        st.header("📋 Processing Log")
        
        if st.session_state.processing_log:
            log_container = st.container(height=400)
            with log_container:
                for log_entry in st.session_state.processing_log:
                    st.text(log_entry)
        else:
            st.info("No processing activity yet")
    
    # Footer
    st.divider()
    st.caption("Built with Docling, Streamlit, and AstraDB")


if __name__ == "__main__":
    main()

# Made with Bob
