"""OnGi Radar 메인 파이프라인.
수집 → 중복제거 → 점수 → 임계값 필터 → 저장 → 다이제스트 발송.
로컬 실행:  python main.py
"""
import yaml
from datetime import date

from collectors import naver_news, g2b, papers
from pipeline.dedupe import dedupe
from pipeline.score import score_items
from pipeline import store_notion
from digest.build import build_html
from deliver import email_send


def load_cfg(path="config.yaml"):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    cfg = load_cfg()
    look = cfg["lookback_days"]

    # 1) 수집 -------------------------------------------------------
    news_q = (cfg["competitors"]["direct"] + cfg["competitors"]["adjacent"]
              + cfg["category_keywords"])
    items = []
    items += naver_news.collect(news_q, look)
    items += g2b.collect(cfg["g2b_keywords"], look)
    items += papers.collect(cfg["paper_topics"], look)

    # 2) 중복제거 ---------------------------------------------------
    items = dedupe(items)

    # 3) 점수 -------------------------------------------------------
    items = score_items(items, cfg["model"])

    # 4) 임계값 필터 -------------------------------------------------
    passed = [i for i in items if i.score >= cfg["score_threshold"]]
    print(f"[filter] {len(items)} -> {len(passed)} (>= {cfg['score_threshold']})")

    if not passed:
        print("이번 주 임계값 통과 항목 없음. 종료.")
        return

    # 5) 저장 -------------------------------------------------------
    if cfg["delivery"]["notion"]:
        store_notion.save(passed)

    # 6) 다이제스트 발송 ---------------------------------------------
    if cfg["delivery"]["email"]:
        html = build_html(passed)
        urgent = sum(1 for i in passed if i.action == "긴급검토")
        subj = f"[온기 레이더] {date.today()} 주간 브리프 · {len(passed)}건"
        if urgent:
            subj = f"⚠{urgent} " + subj
        email_send.send(html, subj)


if __name__ == "__main__":
    main()
