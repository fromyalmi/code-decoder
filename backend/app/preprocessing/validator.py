import tiktoken

from app.preprocessing.code_cleaner import CleanedCode

_ENCODING = tiktoken.get_encoding("cl100k_base")
_RAW_TOKEN_LIMIT = 4_000
_PROCESSED_LINE_LIMIT = 200


class InputTooLarge(Exception):
    pass


def check_raw_size(code: str) -> None:
    if len(_ENCODING.encode(code)) > _RAW_TOKEN_LIMIT:
        raise InputTooLarge("🦜 코드가 너무 길어 — 4,000토큰 이하로 부탁해")


def check_processed_lines(cleaned: CleanedCode) -> None:
    if len(cleaned.mapping) > _PROCESSED_LINE_LIMIT:
        raise InputTooLarge("🦜 실질 코드가 너무 길어 — 200줄 이하로 부탁해")
