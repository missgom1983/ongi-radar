"""온기 관점 관련도 점수 엔진 — 항목별로 score/bucket/so_what/action 생성.
필요 환경변수: ANTHROPIC_API_KEY
"""
import os
import json
from anthropic import Anthropic
from collectors.base import Item

SYSTEM = """너는 '온기'의 전략 애널리스트다.
온기 = 기억 보존형 시니어케어 구독 서비스. 성인 자녀(40~60대)가 결제하고 노인 부모가 정기 전화를 받으며,
케어 신호와 생애 기억을 함께 수집해 주간 다이제스트를 자녀에게 전달한다.
포지셔닝: '케어 회사가 아니라 기억 회사'. 북극성 지표: 부모 90일 능동 참여율.
최우선 감시 대상:
1) 와플랫·효돌의 B2G(지자체 돌봄) 확산  2) 펫로스/고인 AI 영상 기능의 윤리·법무 리스크
3) StoryWorth·Remento 등 기억보존 B2C  4) 음성·노인 데이터 관련 개인정보 규제

각 항목을 평가해 아래 JSON만 출력한다(설명·마크다운 금지):
{"score": 0-100 정수(온기 전략 관련도),
 "bucket": "직접경쟁"|"인접"|"카테고리신호"|"논문근거"|"규제·법무",
 "so_what": "온기에 주는 의미 한 줄(한국어, 40자 내외)",
 "action": "무시"|"모니터링"|"피치덱반영"|"긴급검토"}"""


def score_items(items: list[Item], model: str) -> list[Item]:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        print("[score] ANTHROPIC_API_KEY 없음 — 점수 0으로 통과")
        return items
    client = Anthropic(api_key=key)

    for it in items:
        user = (f"[소스] {it.source}\n[수집태그] {it.raw_tag}\n"
                f"[제목] {it.title}\n[요지] {it.snippet[:600]}")
        try:
            resp = client.messages.create(
                model=model, max_tokens=200,
                system=SYSTEM,
                messages=[{"role": "user", "content": user}],
            )
            txt = "".join(b.text for b in resp.content if b.type == "text")
            txt = txt.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            d = json.loads(txt)
            it.score = int(d.get("score", 0))
            it.bucket = d.get("bucket", "")
            it.so_what = d.get("so_what", "")
            it.action = d.get("action", "")
        except Exception as e:
            print(f"[score] 실패: {it.title[:30]}… {e}")
            it.score = 0
    print(f"[score] {len(items)}건 채점 완료")
    return items
