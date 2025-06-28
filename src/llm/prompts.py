from langsmith import Client

client = Client()


newsletter_prompt = client.pull_prompt("newsletter-prompt")

super_chat_prompt = client.pull_prompt("super_chat_prompt")
super_chat_conversation_title_prompt = client.pull_prompt(
    "super_chat_conversation_title_prompt",
)
