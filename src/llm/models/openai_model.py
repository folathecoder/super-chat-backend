from langchain_openai import ChatOpenAI

# Default model to use
model = "gpt-4o-mini"

# Token limits for various OpenAI models
MODEL_TOKEN_LIMITS = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4o-2024-05-13": 128000,
    "gpt-4-turbo-2024-04-09": 128000,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-1106": 16384,
}


async def async_get_openai_model(temperature=0.5, model=model):
    """
    Asynchronously instantiate a ChatOpenAI model with specified temperature and model name.

    Args:
        temperature (float): Sampling temperature for response randomness.
        model (str): Model name to use.

    Returns:
        ChatOpenAI: An async-compatible ChatOpenAI instance.
    """
    return ChatOpenAI(temperature=temperature, model=model, streaming=True)


def get_openai_model(temperature=0.1, model=model):
    """
    Instantiate a synchronous ChatOpenAI model with specified temperature and model name.

    Args:
        temperature (float): Sampling temperature for response randomness.
        model (str): Model name to use.

    Returns:
        ChatOpenAI: A ChatOpenAI instance.
    """
    return ChatOpenAI(temperature=temperature, model=model)
