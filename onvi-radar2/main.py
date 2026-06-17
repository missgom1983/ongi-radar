"""OnVi Radar v2 (스마트) 메인 파이프라인.
수집 → 중복제거 → 🧠메모리·델타 → 점수 → 필터 → ✍️에디터종합 → 🎯피치초안 → 저장/발송.
로컬 실행:  python main.py
"""
import yaml
from datetime import date

from collectors import naver_news, g2b, papers, kipris, gov_grants
from pipeline.dedupe import dedupe
from pipeline import memory
from pipeline.score import score_items
from pipeline import editor as editor_mod
from pipeline import store_notion
from digest.build import build_html
from digest import pitch as pitch_mod
from deliver import email_send


def load_cfg(path="config.yaml"):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    cfg = load_cfg()
    look = cfg["lookback_days"]
    comp_all = cfg["competitors"]["direct"] + cfg["competitors"]["adjacent"]

    # 1) 수집 (뉴스 + 투자·채용 신호 + 입찰 + 논문 + 특허) -------------
    news_q = comp_all + cfg["category_keywords"] + cfg.get("signal_keywords", [])
    items = []
    items += naver_news.collect(news_q, look)
    items += g2b.collect(cfg["g2b_keywords"], look)
    items += papers.collect(cfg["paper_topics"], look)
    items += kipris.collect(cfg.get("patent_applicants", []))
    items += gov_grants.collect(cfg.get("grant_keywords", []))

    # 2) 중복제거 ---------------------------------------------------
    items = dedupe(items)

    # 3) 🧠 메모리·델타 (신규/지속 + 추세) ---------------------------
    smart = cfg.get("smart", {})
    state, trend = (None, [])
    if smart.get("memory"):
        state, trend = memory.apply_delta(items, comp_all)

    # 4) 점수 + 필터 ------------------------------------------------
    items = score_items(items, cfg["model"])
    passed = [i for i in items if i.score >= cfg["score_threshold"]]
    print(f"[filter] {len(items)} -> {len(passed)} (>= {cfg['score_threshold']})")

    # 5) ✍️ 에디터 종합 --------------------------------------------
    ed = editor_mod.synthesize(passed, trend, cfg["model"]) if smart.get("editor") else {}

    # 6) 다이제스트 HTML (에디터·추세·델타 포함) → 항상 파일 저장 -----
    html = build_html(passed, editor=ed, trend=trend) if passed else "<p>이번 주 통과 항목 없음</p>"
    with open("digest.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[digest] digest.html 저장 ({len(passed)}건)")

    # 7) 🎯 피치 초안 ----------------------------------------------
    if smart.get("pitch"):
        pitch_mod.generate(passed, cfg["model"])

    # 8) 메모리 저장(다음 주 델타 기준) ------------------------------
    if smart.get("memory") and state is not None:
        memory.save(state, items)

    if not passed:
        return

    # 9) 저장 / 발송 (선택) -----------------------------------------
    if cfg["delivery"]["notion"]:
        store_notion.save(passed)
    if cfg["delivery"]["email"]:
        urgent = sum(1 for i in passed if i.action == "긴급검토")
        subj = f"[온비 레이더] {date.today()} 주간 브리프 · {len(passed)}건"
        if ed.get("headline"):
            subj = f"[{ed.get('threat','중')}] " + subj
        email_send.send(html, subj, attachments=["pitch_draft.md"])


if __name__ == "__main__":
    main()
