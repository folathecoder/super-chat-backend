from src.llm.prompts.prompts import super_chat_prompt
from src.llm.models.openai_model import get_openai_model
from src.models.prompt import PromptMessages

user_prompt_llm = get_openai_model().with_structured_output(PromptMessages)

user_prompt_chain = (
    {
        "conversation_titles": lambda x: x["conversation_titles"],
        "user_profile": lambda x: x["user_profile"],
    }
    | super_chat_prompt
    | user_prompt_llm
    | {"prompts": lambda x: x.prompts}
)
