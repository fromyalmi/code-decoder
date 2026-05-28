import io
import tokenize
from dataclasses import dataclass


@dataclass
class CleanedCode:
    code: str
    mapping: dict[int, int]
    tagged: str


def clean(code: str, language: str = "python") -> CleanedCode:
    lines = code.splitlines()
    comment_lines: set[int] = set()
    docstring_lines: set[int] = set()
    inline_comment_col: dict[int, int] = {}

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
        for tok_type, _, tok_start, tok_end, _ in tokens:
            row, col = tok_start
            if tok_type == tokenize.COMMENT:
                before = lines[row - 1][:col].strip()
                if before:
                    inline_comment_col[row] = col
                else:
                    comment_lines.add(row)
            elif tok_type == tokenize.STRING:
                stripped = lines[row - 1].strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    for r in range(row, tok_end[0] + 1):
                        docstring_lines.add(r)
    except tokenize.TokenError:
        pass

    real_lines: list[tuple[int, str]] = []
    mapping: dict[int, int] = {}

    for orig, line in enumerate(lines, start=1):
        if orig in comment_lines or orig in docstring_lines:
            continue
        if orig in inline_comment_col:
            line = line[: inline_comment_col[orig]].rstrip()
        if not line.strip():
            continue
        real_no = len(real_lines) + 1
        mapping[orig] = real_no
        real_lines.append((orig, line))

    cleaned = "\n".join(line for _, line in real_lines)
    tagged = "\n".join(f"L{orig}: {line}" for orig, line in real_lines)

    return CleanedCode(code=cleaned, mapping=mapping, tagged=tagged)
