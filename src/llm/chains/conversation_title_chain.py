from src.llm.prompts.prompts import super_chat_conversation_title_prompt
from src.llm.models.openai_model import get_openai_model
from src.models.conversation import ConversationTitle

chat_conversation_title_llm = get_openai_model().with_structured_output(
    ConversationTitle
)

chat_conversation_title_chain = (
    {
        "context": lambda x: x["context"],
    }
    | super_chat_conversation_title_prompt
    | chat_conversation_title_llm
    | {"title": lambda x: x.title}
)
