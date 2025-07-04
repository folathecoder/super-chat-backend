from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.document_transformers import LongContextReorder
from src.llm.models.openai_model import get_openai_model
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
base_retriever = vector_store.as_retriever()


# Setup LLM and compressor
llm = get_openai_model(temperature=0.0)
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_retriever=base_retriever, base_compressor=compressor
)

# Reorder context to prevent "Lost in the Middle" effect
reordering = LongContextReorder()
