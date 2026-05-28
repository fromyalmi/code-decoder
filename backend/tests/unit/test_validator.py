import pytest

from app.preprocessing.code_cleaner import CleanedCode
from app.preprocessing.validator import (
    InputTooLarge,
    check_processed_lines,
    check_raw_size,
)


class TestCheckRawSize:
    def test_passes_when_code_is_under_4000_tokens(self):
        check_raw_size("print('hi')")

    def test_raises_when_code_exceeds_4000_tokens(self):
        with pytest.raises(InputTooLarge):
            check_raw_size("x = 1\n" * 3000)


def _make_cleaned(n_lines: int) -> CleanedCode:
    lines = [f"x{i} = {i}" for i in range(n_lines)]
    code = "\n".join(lines)
    mapping = {i + 1: i + 1 for i in range(n_lines)}
    tagged = "\n".join(f"L{i + 1}: x{i} = {i}" for i in range(n_lines))
    return CleanedCode(code=code, mapping=mapping, tagged=tagged)


class TestCheckProcessedLines:
    def test_passes_when_processed_lines_under_200(self):
        check_processed_lines(_make_cleaned(100))

    def test_raises_when_processed_lines_exceed_200(self):
        with pytest.raises(InputTooLarge):
            check_processed_lines(_make_cleaned(201))

    def test_passes_when_processed_lines_exactly_200(self):
        check_processed_lines(_make_cleaned(200))
