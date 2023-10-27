import openai


def initialize_openai(openai_api_key: str) -> bool:
    if not openai_api_key:
        return False
    openai.api_key = openai_api_key
    return True
