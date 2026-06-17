"""🧠 메모리·델타 엔진.
- 이미 본 항목(신규/지속) 자동 태깅
- 경쟁사별 주간 등장 횟수 누적 → 가속/둔화 추세 감지
상태는 state/history.json에 저장(워크플로가 매주 레포에 커밋해 영속화).
"""
import os
import json
from datetime import date

STATE_PATH = "state/history.json"


def _load() -> dict:
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"seen": {}, "weekly_counts": {}}


def apply_delta(items, competitors: list[str]):
    """각 항목에 신규/지속 태깅. 이번 주 경쟁사 등장수 집계. (state, trend) 반환."""
    state = _load()
    seen = state.get("seen", {})
    today = date.today().isoformat()

    counts = {}
    for it in items:
        k = it.key()
        if k in seen:
            it.delta, it.first_seen = "지속", seen[k]
        else:
            it.delta, it.first_seen = "신규", today
        # 경쟁사 등장 집계(제목 기준)
        for c in competitors:
            if c in it.title:
                counts[c] = counts.get(c, 0) + 1

    # 추세 = 직전 주 대비 증감
    weekly = state.get("weekly_counts", {})
    prev_week = max([d for d in weekly], default=None)
    trend = []
    for c, n in sorted(counts.items(), key=lambda x: -x[1]):
        prev = weekly.get(prev_week, {}).get(c, 0) if prev_week else 0
        if n > prev:
            trend.append(f"📈 {c} 가속 ({prev}→{n})")
        elif n < prev and prev:
            trend.append(f"📉 {c} 둔화 ({prev}→{n})")
        else:
            trend.append(f"➡️ {c} ({n})")

    state["_today"], state["_counts"] = today, counts
    state["seen"], state["weekly_counts"] = seen, weekly
    return state, trend


def save(state, items):
    """이번 주 본 항목·집계를 누적 저장."""
    today = state.get("_today", date.today().isoformat())
    for it in items:
        state["seen"].setdefault(it.key(), it.first_seen or today)
    state["weekly_counts"][today] = state.get("_counts", {})
    os.makedirs("state", exist_ok=True)
    state.pop("_today", None); state.pop("_counts", None)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"[memory] 누적 {len(state['seen'])}건 저장")
