from src.llm.prompts.prompts import newsletter_prompt
from src.llm.models.openai_model import get_openai_model
from src.models.newsletter import Newsletter

# Initialize OpenAI model configured to output structured Newsletter data
newsletter_llm = get_openai_model().with_structured_output(Newsletter)

# Define the newsletter generation chain:
# 1. Extract input fields from data dict
# 2. Pass through newsletter prompt
# 3. Generate structured newsletter with the LLM
# 4. Extract 'headline' and 'body' fields from the generated Newsletter object
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
