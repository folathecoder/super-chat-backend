from src.llm.chains.newsletter_chain import newsletter_chain
from src.models.newsletter import CreateNewsletter, Newsletter


def generate_newsletter(data: CreateNewsletter) -> Newsletter:
    newsletter_data = data.model_dump()
    return newsletter_chain.invoke(newsletter_data)
