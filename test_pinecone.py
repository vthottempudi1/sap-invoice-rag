"""Quick test to check Pinecone connection and data"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_INDEX = "n8n-s4hana-new"
PINECONE_NAMESPACE = "invoice-documents"

print("Testing Pinecone connection...")
print(f"Index: {PINECONE_INDEX}")
print(f"Namespace: {PINECONE_NAMESPACE}")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Get index stats
try:
    index = pc.Index(PINECONE_INDEX)
    stats = index.describe_index_stats()
    print(f"\nIndex Statistics:")
    print(f"Total vectors: {stats.total_vector_count}")
    print(f"Namespaces: {list(stats.namespaces.keys())}")
    
    for ns, info in stats.namespaces.items():
        print(f"  '{ns}': {info.vector_count} vectors")
except Exception as e:
    print(f"Error: {e}")

# Try querying with embeddings
print("\nTesting vector store query...")
try:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        dimensions=512,
        api_key=OPENAI_API_KEY
    )
    
    vectorstore = PineconeVectorStore(
        index_name=PINECONE_INDEX,
        embedding=embeddings,
        namespace=PINECONE_NAMESPACE,
        pinecone_api_key=PINECONE_API_KEY
    )
    
    # Try a simple search
    results = vectorstore.similarity_search("invoice", k=5)
    print(f"Found {len(results)} documents")
    
    if results:
        print(f"\nFirst result:")
        print(f"Content: {results[0].page_content[:200]}...")
        print(f"Metadata: {results[0].metadata}")
    
except Exception as e:
    print(f"Error: {e}")
