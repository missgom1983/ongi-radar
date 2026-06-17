"""네이버 뉴스 검색 API 수집기.
필요 환경변수: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
발급: https://developers.naver.com/apps  (검색 > 뉴스 API)

법무 메모: 기사 '제목 + 링크 + 자체 요지'만 저장한다. 본문 전문 저장·재배포 금지(저작권).
"""
import os
import re
import html
from datetime import datetime, timedelta
import requests
from dateutil import parser as dtparser
from .base import Item

ENDPOINT = "https://openapi.naver.com/v1/search/news.json"


def _clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    return html.unescape(s).strip()


def collect(queries: list[str], lookback_days: int) -> list[Item]:
    cid, secret = os.getenv("NAVER_CLIENT_ID"), os.getenv("NAVER_CLIENT_SECRET")
    if not cid or not secret:
        print("[news] NAVER 키 없음 — 스킵")
        return []

    headers = {"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": secret}
    cutoff = datetime.now().astimezone() - timedelta(days=lookback_days)
    items: list[Item] = []

    for q in queries:
        try:
            r = requests.get(ENDPOINT, headers=headers,
                             params={"query": q, "display": 20, "sort": "date"}, timeout=15)
            r.raise_for_status()
            for it in r.json().get("items", []):
                try:
                    pub = dtparser.parse(it["pubDate"])
                    if pub < cutoff:
                        continue
                    pub_s = pub.strftime("%Y-%m-%d")
                except Exception:
                    pub_s = None
                items.append(Item(
                    source="news",
                    title=_clean(it.get("title", "")),
                    url=it.get("originallink") or it.get("link", ""),
                    published=pub_s,
                    snippet=_clean(it.get("description", "")),
                    raw_tag=q,
                ))
        except Exception as e:
            print(f"[news] '{q}' 실패: {e}")
    print(f"[news] {len(items)}건 수집")
    return items
