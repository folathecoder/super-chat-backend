from src.llm.chains.newsletter_chain import newsletter_chain
from src.models.newsletter import CreateNewsletter, Newsletter


def generate_newsletter(data: CreateNewsletter) -> Newsletter:
    """
    Generate a newsletter using the provided data.

    Args:
        data (CreateNewsletter): Input data to generate the newsletter.

    Returns:
        Newsletter: Generated newsletter object.
    """

    newsletter_data = data.model_dump()
    return newsletter_chain.invoke(newsletter_data)
