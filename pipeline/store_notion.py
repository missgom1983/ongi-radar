"""Notion DB 누적 저장.
필요 환경변수: NOTION_TOKEN, NOTION_DB_ID
세팅:
 1) https://www.notion.so/my-integrations 에서 내부 통합 생성 → 토큰 복사
 2) Notion에서 빈 데이터베이스 생성 후 우상단 ... > 연결 > 통합 추가
 3) DB URL에서 32자리 ID 추출 (notion.so/<workspace>/<DB_ID>?v=...)

DB 속성(이름/타입) 권장:
 제목(Title), 점수(Number), 분류(Select), So-What(Text),
 액션(Select), 소스(Select), 날짜(Date), 링크(URL)
"""
import os
import requests

API = "https://api.notion.com/v1/pages"


def save(items, db_id_env="NOTION_DB_ID"):
    token, db = os.getenv("NOTION_TOKEN"), os.getenv(db_id_env)
    if not token or not db:
        print("[notion] 토큰/DB ID 없음 — 스킵")
        return
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    ok = 0
    for it in items:
        props = {
            "제목":   {"title": [{"text": {"content": it.title[:200]}}]},
            "점수":   {"number": it.score},
            "분류":   {"select": {"name": it.bucket or "기타"}},
            "So-What": {"rich_text": [{"text": {"content": it.so_what[:300]}}]},
            "액션":   {"select": {"name": it.action or "모니터링"}},
            "소스":   {"select": {"name": it.source}},
            "링크":   {"url": it.url or None},
        }
        if it.published:
            props["날짜"] = {"date": {"start": it.published}}
        try:
            r = requests.post(API, headers=headers,
                              json={"parent": {"database_id": db}, "properties": props},
                              timeout=15)
            r.raise_for_status()
            ok += 1
        except Exception as e:
            print(f"[notion] 저장 실패: {it.title[:30]}… {e}")
    print(f"[notion] {ok}건 저장")
