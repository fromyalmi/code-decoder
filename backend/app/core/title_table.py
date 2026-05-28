from typing import Optional

# (stage, emoji, label, next_threshold) — FR-GAME-003 B 표준 임계값: 10/30/100/100+
TITLE_STAGES: list[tuple[int, str, str, Optional[int]]] = [
    (1, "🥚🦜", "알 속의 코뉴", 10),
    (2, "🪶🦜", "첫 비행에 성공한 코뉴", 30),
    (3, "🌲🦜", "나무 위의 코뉴", 100),
    (4, "🎩🦜", "전설의 코뉴", None),
]


def get_title(analysis_count_total: int) -> dict:
    current = TITLE_STAGES[0]
    for stage in TITLE_STAGES:
        threshold = stage[3]
        if threshold is None or analysis_count_total < threshold:
            current = stage
            break
    return {
        "stage": current[0],
        "emoji": current[1],
        "label": current[2],
        "next_threshold": current[3],
    }
