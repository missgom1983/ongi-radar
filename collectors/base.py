"""수집 항목의 공통 규격. 모든 collector는 Item 리스트를 반환한다."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Item:
    source: str                 # "news" | "g2b" | "paper_openalex" | "paper_arxiv"
    title: str
    url: str
    published: Optional[str] = None      # ISO 날짜 문자열
    snippet: str = ""                    # 요지/초록 (원문 인용 금지, 요지만)
    raw_tag: str = ""                    # 수집 시 분류 태그 (예: 논문 토픽)

    # --- 점수 엔진이 채우는 필드 ---
    score: int = 0                       # 0~100 온기 관련도
    bucket: str = ""                     # 직접경쟁/인접/카테고리신호/논문근거/규제·법무
    so_what: str = ""                    # 온기 관점 1줄
    action: str = ""                     # 무시/모니터링/피치덱반영/긴급검토

    def key(self) -> str:
        """중복 제거 키: URL 우선, 없으면 정규화 제목."""
        if self.url:
            return self.url.strip().lower().rstrip("/")
        return "".join(self.title.lower().split())

    def dict(self):
        return asdict(self)


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")
