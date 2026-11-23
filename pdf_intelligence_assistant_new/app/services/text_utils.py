from __future__ import annotations

import unicodedata


def tokenize(text: str) -> list[str]:
    """Unicode-aware tokenizer that keeps combining marks attached to words."""
    tokens: list[str] = []
    current: list[str] = []
    for char in text.casefold():
        category = unicodedata.category(char)
        if category[0] in {"L", "M", "N"}:
            current.append(char)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return tokens
