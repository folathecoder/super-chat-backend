from src.models.prompt import Prompt, PromptMessages


def prompt_schema(prompt: Prompt):
    return {
        "id": str(prompt["_id"]),
        "userId": prompt["userId"],
        "prompts": prompt["prompts"],
        "createdAt": prompt["createdAt"],
        "updatedAt": prompt["updatedAt"],
    }


def prompt_messages_schema(prompt_messages: PromptMessages):
    return {
        "prompts": prompt_messages["prompts"],
    }
