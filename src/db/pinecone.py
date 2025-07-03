from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from src.core.config import ENV_VARS

# Initialize OpenAI embeddings model for vectorizing text
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=512,
)

# Initialize Pinecone client with API key from env vars
pinecone = Pinecone(api_key=ENV_VARS["PINECONE_API_KEY"])

# Connect to the Pinecone index named "super-chat"
index = pinecone.Index("super-chat-store")

# Create a LangChain Pinecone vector store instance to manage embeddings and search
vector_store = PineconeVectorStore(embedding=embeddings, index=index)
