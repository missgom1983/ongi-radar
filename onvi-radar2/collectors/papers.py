"""논문 수집기 — OpenAlex(1차) + arXiv(2차). paper-downloader 스킬과 동일 소스.
키 불필요. 여기서는 메타데이터+초록 요지만 수집(주간 다이제스트용).
풀 PDF가 필요하면 플래깅된 제목으로 paper-downloader 스킬을 별도 실행한다.

법무 메모: 초록은 원문 그대로가 아니라 요지로 재서술해 저장(저작권). OA 링크만 노출.
"""
import requests
from datetime import datetime, timedelta
from .base import Item

OPENALEX = "https://api.openalex.org/works"


def _from_openalex(tag: str, query: str, since: str, n: int) -> list[Item]:
    out: list[Item] = []
    try:
        r = requests.get(OPENALEX, params={
            "search": query,
            "filter": f"from_publication_date:{since}",
            "sort": "publication_date:desc",
            "per_page": n,
            "mailto": "radar@onvi.example",
        }, timeout=20)
        r.raise_for_status()
        for w in r.json().get("results", []):
            # 초록은 inverted index → 짧은 요지로만 환원
            abx = w.get("abstract_inverted_index") or {}
            words = sorted(((pos, tok) for tok, ps in abx.items() for pos in ps))
            abstract = " ".join(t for _, t in words)[:500]
            oa = (w.get("open_access") or {}).get("oa_url")
            out.append(Item(
                source="paper_openalex",
                title=w.get("title") or "",
                url=oa or w.get("id", ""),
                published=w.get("publication_date"),
                snippet=abstract,
                raw_tag=tag,
            ))
    except Exception as e:
        print(f"[paper:openalex] '{tag}' 실패: {e}")
    return out


def _from_arxiv(tag: str, query: str, n: int) -> list[Item]:
    import xml.etree.ElementTree as ET
    out: list[Item] = []
    try:
        r = requests.get("http://export.arxiv.org/api/query", params={
            "search_query": f"all:{query}", "sortBy": "submittedDate",
            "sortOrder": "descending", "max_results": n,
        }, timeout=20)
        r.raise_for_status()
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for e in ET.fromstring(r.text).findall("a:entry", ns):
            out.append(Item(
                source="paper_arxiv",
                title=(e.findtext("a:title", "", ns) or "").strip(),
                url=e.findtext("a:id", "", ns),
                published=(e.findtext("a:published", "", ns) or "")[:10],
                snippet=(e.findtext("a:summary", "", ns) or "").strip()[:500],
                raw_tag=tag,
            ))
    except Exception as e:
        print(f"[paper:arxiv] '{tag}' 실패: {e}")
    return out


def collect(topics: list[dict], lookback_days: int) -> list[Item]:
    # 논문은 게시 주기가 길어 lookback을 넉넉히(최소 30일)
    days = max(lookback_days, 30)
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    items: list[Item] = []
    for t in topics:
        items += _from_openalex(t["tag"], t["query"], since, n=5)
        items += _from_arxiv(t["tag"], t["query"], n=3)
    print(f"[paper] {len(items)}건 수집")
    return items
