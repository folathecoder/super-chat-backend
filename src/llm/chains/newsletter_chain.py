from src.llm.prompts import newsletter_prompt
from src.llm.models.openai_model import get_openai_model
from src.models.newsletter import Newsletter


newsletter_llm = get_openai_model().with_structured_output(Newsletter)


newsletter_chain = (
    {
        "firstName": lambda x: x["firstName"],
        "categories": lambda x: x["categories"],
        "tone": lambda x: x["tone"],
        "occupation": lambda x: x["occupation"],
        "reason": lambda x: x["reason"],
    }
    | newsletter_prompt
    | newsletter_llm
    | {
        "headline": lambda x: x.headline,
        "body": lambda x: x.body,
    }
)
