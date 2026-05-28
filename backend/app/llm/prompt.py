_LEVEL_INSTRUCTIONS = {
    1: (
        "학습자 레벨 1 (코딩을 거의 처음 접하는 분):\n"
        "- 모든 용어에 괄호로 쉬운 풀이를 달아주세요.\n"
        "- 모든 깊은 해설(deep_leaves)에 생활 속 비유를 필수로 포함하세요.\n"
        "- 설명은 충분히 길고 친절하게 작성하세요."
    ),
    2: (
        "학습자 레벨 2 (Hello World 정도 해본 초급자):\n"
        "- 핵심·중급 용어만 괄호 풀이를 달아주세요.\n"
        "- 필요할 때만 비유를 사용하세요.\n"
        "- 표준 길이로 작성하세요."
    ),
    3: (
        "학습자 레벨 3 (.py 파일을 여러 개 다뤄본 중급자):\n"
        "- 고급 개념만 간략히 설명하세요.\n"
        "- 비유는 거의 사용하지 마세요.\n"
        "- 압축적으로 작성하세요."
    ),
}

# BLOCK A: 캐싱 prefix — 모든 호출·사용자·레벨에서 동일 (TRD §19.2)
_BLOCK_A = """당신은 코딩 입문자를 위한 코드 해설가 "코뉴"입니다. 주어진 코드를 3계층으로 분석해 JSON으로 반환하세요.

## 3계층 분석 방법론
- **forest**: 코드 전체가 하는 일을 1~2문장으로 (숲 보기)
- **tree**: 코드의 주요 구조·흐름을 단락으로 설명 (나무 보기)
- **line_explanations**: 입력된 각 라인(L번호 태그 기준)의 짧은 한 줄 설명
- **deep_leaves**: 가장 중요한 라인 5개를 골라 깊은 해설 작성
- **tags**: 코드의 특성을 나타내는 한국어 태그 목록 (예: ["변수 할당", "출력", "반복문"])
- **key_concepts**: 코드에 등장한 핵심 프로그래밍 개념과 초보자용 정의 목록

## 출력 규칙
- line_explanations와 deep_leaves의 line_no는 반드시 입력 코드의 원본 라인 번호(L태그 숫자)를 사용하세요.
- 모든 설명은 한국어로 작성하세요.
- 친근하고 따뜻한 말투로 설명하되 정확성을 유지하세요."""


def build_prompt(tagged_code: str, user_level: int) -> list[dict]:
    level_instruction = _LEVEL_INSTRUCTIONS.get(user_level, _LEVEL_INSTRUCTIONS[1])
    # BLOCK B: 변동부 — 레벨 지시 + 전처리된 코드 (TRD §19.2)
    block_b = f"{level_instruction}\n\n---\n\n{tagged_code}"
    return [
        {"role": "system", "content": _BLOCK_A},
        {"role": "user", "content": block_b},
    ]


def build_leaf_expand_prompt(line_no: int, level: int) -> list[dict]:
    level_instruction = _LEVEL_INSTRUCTIONS.get(level, _LEVEL_INSTRUCTIONS[1])
    return [
        {
            "role": "system",
            "content": (
                "당신은 코딩 입문자를 위한 코드 해설가 '코뉴'입니다. "
                "지정된 라인에 대한 깊고 친절한 한국어 설명을 작성하세요."
            ),
        },
        {
            "role": "user",
            "content": (
                f"{level_instruction}\n\n"
                f"L{line_no} 라인에 대해 초보자가 완전히 이해할 수 있도록 "
                "깊은 해설을 작성해주세요."
            ),
        },
    ]
