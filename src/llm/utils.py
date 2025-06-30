from src.llm.models.openai_model import MODEL_TOKEN_LIMITS


def get_max_prompt_tokens(model_name: str, output_tokens: int = 1024):
    return MODEL_TOKEN_LIMITS[model_name] - output_tokens
