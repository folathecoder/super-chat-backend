from langsmith import Client

# Initialize LangSmith client
client = Client()

# Pull prompts from LangSmith by their IDs
newsletter_prompt = client.pull_prompt("newsletter-prompt")
super_chat_prompt = client.pull_prompt("super_chat_prompt")
super_chat_conversation_title_prompt = client.pull_prompt(
    "super_chat_conversation_title_prompt",
)
super_chat_document_context = client.pull_prompt(
    "super_chat_document_context",
)
