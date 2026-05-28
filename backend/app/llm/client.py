from app.core.exceptions import LLMFailure


def call_analysis(messages: list[dict], max_tokens: int = 8000) -> dict:
    raise LLMFailure("OpenAI not wired")
