from src.llm.models.openai_model import MODEL_TOKEN_LIMITS


def get_max_prompt_tokens(model_name: str, output_tokens: int = 1024):
    """
    Calculate the maximum number of tokens allowed in the prompt
    given a model's total token limit and desired output tokens.

    Args:
        model_name (str): Name of the model.
        output_tokens (int): Number of tokens expected in the output (default 1024).

    Returns:
        int: Maximum tokens allowed for the prompt.
    """
    return MODEL_TOKEN_LIMITS[model_name] - output_tokens
