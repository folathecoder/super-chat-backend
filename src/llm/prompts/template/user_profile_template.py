from langchain.prompts import PromptTemplate


user_profile_template = PromptTemplate.from_template(
    """
    Name: {firstName} {lastName}
    Occupation: {occupation}
    Industry: {industry}
    Interests: {interests}
    Goals: {goals}
    Expertise Areas: {expertiseAreas}

    Using this information, respond to the user in a way that is tailored to their background, interests, and goals.
    """
)
