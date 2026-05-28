import pytest

from app.preprocessing.validator import InputTooLarge, check_raw_size


class TestCheckRawSize:
    def test_passes_when_code_is_under_4000_tokens(self):
        check_raw_size("print('hi')")

    def test_raises_when_code_exceeds_4000_tokens(self):
        with pytest.raises(InputTooLarge):
            check_raw_size("x = 1\n" * 3000)
