def build_prompt(tagged_code: str, user_level: int) -> list[dict]:
    return [
        {
            "role": "system",
            "content": "You are a beginner-friendly Python code explainer.",
        },
        {"role": "user", "content": tagged_code},
    ]
