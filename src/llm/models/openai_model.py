from langchain_openai import ChatOpenAI


async def async_get_openai_model(temperature=0.1, model="gpt-4o-mini"):
    return ChatOpenAI(temperature=temperature, model=model)


def get_openai_model(temperature=0.1, model="gpt-4o-mini"):
    return ChatOpenAI(temperature=temperature, model=model)
