"""URL/정규화 제목 기준 중복 제거."""
from collectors.base import Item


def dedupe(items: list[Item]) -> list[Item]:
    seen, out = set(), []
    for it in items:
        k = it.key()
        if k in seen:
            continue
        seen.add(k)
        out.append(it)
    print(f"[dedupe] {len(items)} -> {len(out)}")
    return out
