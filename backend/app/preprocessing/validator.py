import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")
_RAW_TOKEN_LIMIT = 4_000

_MSG = "🦜 코드가 너무 길어 — 4,000토큰 이하로 부탁해"


class InputTooLarge(Exception):
    pass


def check_raw_size(code: str) -> None:
    if len(_ENCODING.encode(code)) > _RAW_TOKEN_LIMIT:
        raise InputTooLarge(_MSG)
