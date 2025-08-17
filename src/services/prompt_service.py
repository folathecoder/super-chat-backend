from datetime import datetime, timezone, timedelta
from typing import List
from src.schema.prompt_schema import prompt_schema, prompt_messages_schema
from src.models.prompt import Prompt, PromptMessages
from src.db.collections import prompts_collection
from src.services.user_service import get_current_user, user_profile_context
from src.llm.chains.user_prompt_chain import user_prompt_chain
from src.services.conversation_service import get_all_conversations


async def ai_generated_user_prompt() -> PromptMessages:
    user_conversations = await get_all_conversations()
    user_context = await user_profile_context()

    conversation_titles = []

    for conversation in user_conversations:
        conversation_titles.append(conversation["title"])

    prompt_messages: PromptMessages = user_prompt_chain.invoke(
        {
            "conversation_titles": ", ".join(conversation_titles),
            "user_profile": user_context,
        }
    )

    return prompt_messages_schema(prompt_messages)


async def generate_user_prompt() -> Prompt:
    user_prompt = await get_user_prompt()

    # Check if the last updated time was more than 2 hours ago
    def is_stale(updated_at_value) -> bool:
        if isinstance(updated_at_value, str):
            updated_at = datetime.fromisoformat(updated_at_value)
        else:
            updated_at = updated_at_value

        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)

        return datetime.now(timezone.utc) - updated_at > timedelta(minutes=10)

    if not user_prompt or is_stale(user_prompt["updatedAt"]):
        prompt_messages = await ai_generated_user_prompt()
        return await save_user_prompt(prompts=prompt_messages["prompts"])

    return user_prompt


async def get_user_prompt() -> Prompt:
    user = await get_current_user()
    user_prompt = await prompts_collection.find_one({"userId": user["id"]})

    return user_prompt


async def save_user_prompt(prompts: List[str]) -> Prompt:
    user = await get_current_user()
    user_prompt = await get_user_prompt()

    if user_prompt:
        # update an existing user prompt, if available

        update_user_prompt_obj = {
            "prompts": prompts,
            "updatedAt": datetime.now(timezone.utc),
        }

        await prompts_collection.update_one(
            {"userId": user["id"]},
            {"$set": update_user_prompt_obj},
        )

        updated_user_prompt = await get_user_prompt()

        return prompt_schema(updated_user_prompt)

    # create a new user prompt, if not available

    new_user_prompt_obj = {
        "userId": user["id"],
        "prompts": prompts,
        "updatedAt": datetime.now(timezone.utc),
        "createdAt": datetime.now(timezone.utc),
    }

    created_user_prompt = await prompts_collection.insert_one(new_user_prompt_obj)
    new_user_prompt_obj["_id"] = created_user_prompt.inserted_id

    return prompt_schema(new_user_prompt_obj)
