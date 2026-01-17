"""
RAG System using LlamaIndex with Gemini Embeddings
Lightweight - uses API for embeddings (no local model)
"""

import os
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini

load_dotenv()

# Configuration
PERSIST_DIR = "./storage"
DOCS_DIR = "./documents"
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini models
gemini_embedding = GeminiEmbedding(
    api_key=GEMINI_API_KEY,
    model_name="models/text-embedding-004"
)

gemini_llm = Gemini(
    api_key=GEMINI_API_KEY,
    model_name="models/gemini-2.0-flash-exp"
)

# Set global settings
Settings.llm = gemini_llm
Settings.embed_model = gemini_embedding


def build_index(force_rebuild=False):
    """
    Build or load the vector index
    
    Args:
        force_rebuild: If True, rebuild index even if it exists
    
    Returns:
        VectorStoreIndex or None: The loaded or created index, or None if no documents
    """
    print("Initializing RAG system...")
    
    # Create directories if they don't exist
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(PERSIST_DIR, exist_ok=True)
    
    # Check if documents exist
    doc_files = [f for f in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, f))]
    
    if not doc_files:
        print("No documents found in ./documents/")
        print("Please upload documents to enable RAG")
        return None
    
    # Check if we should rebuild
    if force_rebuild and os.path.exists(PERSIST_DIR):
        import shutil
        shutil.rmtree(PERSIST_DIR)
        print("Rebuilding index from scratch...")
    
    # Load or create index
    if not os.path.exists(os.path.join(PERSIST_DIR, "docstore.json")) or force_rebuild:
        # Load documents and create index
        print("Loading documents...")
        try:
            documents = SimpleDirectoryReader(DOCS_DIR).load_data()
            print(f"Loaded {len(documents)} documents")
            
            print("Creating embeddings (using Gemini API)...")
            index = VectorStoreIndex.from_documents(documents)
            
            # Save index
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            print("Index created and saved")
        except Exception as e:
            print(f"Error creating index: {e}")
            return None
    else:
        # Load existing index
        try:
            print("Loading existing index...")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
            print("Index loaded")
        except Exception as e:
            print(f"Error loading index: {e}")
            return None
    
    return index


def query_docs(query: str) -> str:
    """
    Query the document index
    
    Args:
        query: The question to search for
    
    Returns:
        str: The answer from the documents
    """
    print(f"Querying: {query}")
    
    try:
        # Build/load index
        index = build_index()
        
        # Create query engine
        query_engine = index.as_query_engine()
        
        # Query
        response = query_engine.query(query)
        
        # Convert to string
        response_text = str(response)
        print(f"RAG Response: {response_text[:100]}...")
        
        return response_text
        
    except Exception as e:
        error_msg = f"Error querying documents: {str(e)}"
        print(f"{error_msg}")
        return error_msg


def create_sample_docs():
    """Create sample documents for testing"""
    
    sample_content = """
# TechVision Company Information

## Products

### CloudSync Pro
CloudSync Pro is our flagship cloud storage and synchronization solution.

Features:
- 100GB to unlimited storage options
- End-to-end encryption
- Cross-platform sync (Windows, Mac, Linux, iOS, Android)
- File versioning and automatic backup
- Real-time collaboration

Pricing:
- Basic: $9.99/month (100GB)
- Professional: $19.99/month (500GB)
- Enterprise: $49.99/month (Unlimited)

### DataGuard Enterprise
Enterprise-grade data security and backup solution.

Features:
- Military-grade 256-bit AES encryption
- Automated daily backups
- Ransomware protection
- GDPR and HIPAA compliance
- 99.99% uptime guarantee

Pricing:
- Small Business: $29.99/month (up to 10 users)
- Medium Business: $79.99/month (up to 50 users)
- Enterprise: Custom pricing (50+ users)

### TeamConnect
Real-time collaboration and communication platform.

Features:
- Video conferencing (up to 100 participants)
- Screen sharing and whiteboard
- Task management
- Calendar integration
- Mobile apps for iOS and Android

Pricing:
- Free: Up to 5 team members
- Pro: $12.99/user/month (Unlimited members)

## Support

Business Hours: Monday to Friday, 9:00 AM to 6:00 PM EST
Weekend Support: Available for Enterprise customers only
Emergency Support: 24/7 hotline for critical issues

Contact:
- Email: support@techvision.com
- Phone: +1-800-TECH-SUP (1-800-832-4787)
- Live Chat: Available on website

Average Response Time: Under 2 hours during business hours

## Company Information

Founded: 2018
Headquarters: San Francisco, California
Offices: New York, London, Singapore
Customers: 50,000+ businesses worldwide

Certifications:
- SOC 2 Type II certified
- ISO 27001 compliant
- Regular third-party security audits

## Free Trial

All products offer a 30-day free trial with no credit card required.
You can cancel anytime during the trial period.

## Refund Policy

- 30-day money-back guarantee for all plans
- 60-day guarantee for Enterprise customers
- Refunds processed within 5-7 business days
"""
    
    # Save sample document
    sample_file = os.path.join(DOCS_DIR, "company_info.txt")
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print(f"Created sample document: {sample_file}")


# Test function
if __name__ == "__main__":
    print("="*60)
    print("Testing RAG System with LlamaIndex")
    print("="*60)
    print()
    
    # Test queries
    test_queries = [
        "What are the pricing plans for CloudSync Pro?",
        "What are your business hours?",
        "Tell me about DataGuard Enterprise features",
    ]
    
    for query in test_queries:
        print(f"\nQuestion: {query}")
        print("-" * 60)
        answer = query_docs(query)
        print(f"Answer: {answer}")
        print("=" * 60)