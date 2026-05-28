from app.preprocessing.code_cleaner import clean


class TestCodeCleaner:
    def test_removes_single_line_comments(self):
        result = clean("x = 1  # 주석\ny = 2")
        assert "# 주석" not in result.code

    def test_removes_docstring_comments(self):
        result = clean('"""독스트링"""\nx = 1')
        assert "독스트링" not in result.code

    def test_removes_blank_lines(self):
        result = clean("x = 1\n\n\ny = 2")
        assert all(line.strip() != "" for line in result.code.splitlines())

    def test_preserves_original_line_numbers_in_mapping(self):
        result = clean("x = 1\n# 주석\ny = 2")
        assert result.mapping[1] == 1
        assert result.mapping[3] == 2

    def test_tagged_output_format(self):
        result = clean("x = 1\n# 주석\ny = 2")
        assert result.tagged == "L1: x = 1\nL3: y = 2"
