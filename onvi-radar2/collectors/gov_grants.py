"""💰 정부 지원사업·공고 수집기 — 기업마당(bizinfo) OpenAPI.
온비가 신청할 만한 정부 지원금·투자공고를 키워드로 필터링.
필요 환경변수: BIZINFO_KEY  (기업마당 인증키 crtfcKey)
발급: https://www.bizinfo.go.kr/apiList.do → '지원사업 공고' 사용신청

법무 메모: 공고 제목·소관기관·신청기간·상세URL 등 공개 메타데이터만 저장.
"""
import os
import requests
import xml.etree.ElementTree as ET
from .base import Item

ENDPOINT = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"


def _txt(el, *names):
    for n in names:
        c = el.find(n)
        if c is not None and (c.text or "").strip():
            return c.text.strip()
    return ""


def collect(keywords: list[str]) -> list[Item]:
    key = os.getenv("BIZINFO_KEY")
    if not key:
        print("[grant] BIZINFO_KEY 없음 — 스킵")
        return []

    items: list[Item] = []
    try:
        r = requests.get(ENDPOINT, params={"crtfcKey": key, "dataType": "rss"}, timeout=20)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        for el in root.iter("item"):
            name = _txt(el, "pblancNm", "title")
            if not name:
                continue
            # 온비 관련 키워드 필터 (제목 기준)
            if keywords and not any(k in name for k in keywords):
                continue
            url = _txt(el, "pblancUrl", "link")
            if url.startswith("/"):
                url = "https://www.bizinfo.go.kr" + url
            field = _txt(el, "pldirSportRealmLclasCodeNm", "category")
            jrsd = _txt(el, "jrsdInsttNm")
            period = _txt(el, "reqstBeginEndDe")
            items.append(Item(
                source="grant",
                title=f"[지원사업] {name}",
                url=url,
                published=_txt(el, "creatPnttm", "pubDate")[:10],
                snippet=f"분야:{field} / 소관:{jrsd} / 신청기간:{period}",
                raw_tag="정부지원",
            ))
    except Exception as e:
        print(f"[grant] 실패(키/엔드포인트 확인): {e}")
    print(f"[grant] {len(items)}건 수집")
    return items
