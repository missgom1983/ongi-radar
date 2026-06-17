"""🔍 KIPRIS 특허 수집기 — 경쟁사 특허 출원 = 기술 로드맵 조기 신호.
필요 환경변수: KIPRIS_KEY  (KIPRIS Plus 활용신청: https://plus.kipris.or.kr )
출원인(applicant) 기준으로 최근 공개 특허를 가져온다. 키 없으면 자동 스킵.
"""
import os
import requests
import xml.etree.ElementTree as ET
from .base import Item

# KIPRIS Plus 특허·실용신안 출원인검색 (신청 후 정확한 endpoint로 교체)
ENDPOINT = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/applicantNameSearchInfo"


def collect(applicants: list[str]) -> list[Item]:
    key = os.getenv("KIPRIS_KEY")
    if not key:
        print("[kipris] KIPRIS_KEY 없음 — 스킵")
        return []
    items: list[Item] = []
    for name in applicants:
        try:
            r = requests.get(ENDPOINT, params={
                "applicant": name, "ServiceKey": key, "numOfRows": 10, "pageNo": 1,
            }, timeout=20)
            r.raise_for_status()
            root = ET.fromstring(r.text)
            for it in root.iter("item"):
                title = (it.findtext("inventionTitle") or it.findtext("title") or "").strip()
                if not title:
                    continue
                items.append(Item(
                    source="patent",
                    title=f"[특허출원/{name}] {title}",
                    url=it.findtext("applicationNumber") or "",
                    published=(it.findtext("applicationDate") or "")[:10],
                    snippet=f"출원인: {name}",
                    raw_tag="특허",
                ))
        except Exception as e:
            print(f"[kipris] '{name}' 실패(엔드포인트/키 확인): {e}")
    print(f"[kipris] {len(items)}건 수집")
    return items
