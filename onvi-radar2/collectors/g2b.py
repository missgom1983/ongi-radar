"""나라장터(조달청) 입찰공고정보서비스 수집기 — B2G 확산 추적의 핵심.
필요 환경변수: DATA_GO_KR_KEY  (공공데이터포털 일반 인증키, Decoding 키 권장)
발급: https://www.data.go.kr  '조달청_나라장터 입찰공고정보서비스' 활용신청

용역 입찰공고 기준. 키워드는 공고명(bidNtceNm)으로 필터.
"""
import os
from datetime import datetime, timedelta
import requests
from .base import Item

# 용역 입찰공고 목록 (예시 오퍼레이션 — 포털 신청 후 정확한 endpoint로 교체)
ENDPOINT = "http://apis.data.go.kr/1230000/BidPublicInfoService/getBidPblancListInfoServc"


def collect(keywords: list[str], lookback_days: int) -> list[Item]:
    key = os.getenv("DATA_GO_KR_KEY")
    if not key:
        print("[g2b] DATA_GO_KR_KEY 없음 — 스킵")
        return []

    end = datetime.now()
    start = end - timedelta(days=lookback_days)
    params = {
        "serviceKey": key,
        "pageNo": 1, "numOfRows": 100, "type": "json",
        "inqryDiv": 1,
        "inqryBgnDt": start.strftime("%Y%m%d") + "0000",
        "inqryEndDt": end.strftime("%Y%m%d") + "2359",
    }
    items: list[Item] = []
    try:
        r = requests.get(ENDPOINT, params=params, timeout=20)
        r.raise_for_status()
        rows = (r.json().get("response", {}).get("body", {}).get("items") or [])
        if isinstance(rows, dict):
            rows = rows.get("item", [])
        for row in rows:
            name = row.get("bidNtceNm", "")
            if not any(k in name for k in keywords):
                continue
            items.append(Item(
                source="g2b",
                title=name,
                url=row.get("bidNtceDtlUrl", "") or row.get("bidNtceUrl", ""),
                published=(row.get("bidNtceDt", "") or "")[:10].replace(".", "-"),
                snippet=f"수요기관: {row.get('ntceInsttNm','-')} / 추정가격: {row.get('presmptPrce','-')}",
                raw_tag="B2G입찰",
            ))
    except Exception as e:
        print(f"[g2b] 실패(엔드포인트/키 확인 필요): {e}")
    print(f"[g2b] {len(items)}건 수집")
    return items
