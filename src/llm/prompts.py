from langsmith import Client

client = Client()

newsletter_prompt = client.pull_prompt("newsletter-prompt")
chat_prompt = client.pull_prompt("super_chat_prompt")
