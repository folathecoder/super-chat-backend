from src.db.mongo import db

users_collection = db["users"]
conversations_collection = db["conversations"]
messages_collection = db["messages"]
prompts_collection = db["prompts"]
