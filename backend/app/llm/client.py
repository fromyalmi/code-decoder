from app.core.exceptions import LLMFailure


def call_analysis(messages: list[dict], max_tokens: int = 8000) -> dict:
    raise LLMFailure("OpenAI not wired")


def call_leaf_expand(line_no: int, level: int) -> dict:
    return {"deep_text": f"[stub] line {line_no} 깊은 해설"}
