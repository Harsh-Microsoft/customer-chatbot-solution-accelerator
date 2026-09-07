from __future__ import annotations

import re


def extract_recommended_products(text: str) -> list[str]:
    lines = [line.strip(' -*\t') for line in text.splitlines() if line.strip()]
    picks: list[str] = []
    for line in lines:
        match = re.match(r'^(?:\d+[.)]|[-*])\s*(.+)$', line)
        candidate = match.group(1).strip() if match else line
        if len(candidate) < 2:
            continue
        if candidate not in picks:
            picks.append(candidate)
    return picks[:5]
