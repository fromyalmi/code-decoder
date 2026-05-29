import os
from typing import Optional

from dotenv import load_dotenv

from app.core.exceptions import LLMFailure

load_dotenv()

_MODEL = "gpt-5-mini"
_openai_client = None


def _get_client():
    global _openai_client
    if _openai_client is None:
        import openai

        _openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _openai_client


def call_analysis(messages: list[dict], max_tokens: int = 8000) -> dict:
    from app.llm.parser import LLMAnalysisOutput

    last_exc: Optional[Exception] = None
    for _ in range(3):
        try:
            completion = _get_client().beta.chat.completions.parse(
                model=_MODEL,
                messages=messages,
                max_completion_tokens=max_tokens,
                response_format=LLMAnalysisOutput,
            )
            choice = completion.choices[0]
            if choice.finish_reason == "length" or choice.message.parsed is None:
                raise ValueError("output truncated or parse failed")
            return choice.message.parsed.model_dump()
        except LLMFailure:
            raise
        except Exception as e:
            last_exc = e

    raise LLMFailure(str(last_exc))


def call_leaf_expand(line_no: int, level: int) -> dict:
    from app.llm.prompt import build_leaf_expand_prompt

    messages = build_leaf_expand_prompt(line_no, level)
    last_exc: Optional[Exception] = None
    for _ in range(3):
        try:
            completion = _get_client().chat.completions.create(
                model=_MODEL,
                messages=messages,
                max_tokens=1000,
            )
            deep_text = completion.choices[0].message.content.strip()
            return {"deep_text": deep_text}
        except LLMFailure:
            raise
        except Exception as e:
            last_exc = e

    raise LLMFailure(str(last_exc))
