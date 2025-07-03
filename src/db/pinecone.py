from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from src.core.config import ENV_VARS

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

pinecone = Pinecone(api_key=ENV_VARS["PINECONE_API_KEY"])
index = pinecone.Index("super-chat")

vector_store = PineconeVectorStore(embedding=embeddings, index=index)
