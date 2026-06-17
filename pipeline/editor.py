"""✍️ 에디터 종합 엔진.
통과 항목 전체 + 추세를 Claude가 한 번에 읽고 '이번 주 판단 + 할 일 1개'를 생성.
개별 점수를 '결론'으로 바꾸는 레이어. 필요 환경변수: ANTHROPIC_API_KEY
"""
import os
import json
from anthropic import Anthropic

SYSTEM = """너는 온비(기억 보존형 시니어케어 구독)의 수석 전략 애널리스트다.
이번 주 수집·점수화된 인텔리전스 전체를 종합해 경영진용 결론을 낸다.
와플랫의 B2G 확산, 효돌의 임상근거, 기억보존 B2C, 펫/고인 영상의 윤리·법무 리스크가 핵심 관심사다.
아래 JSON만 출력(마크다운·설명 금지):
{"threat": "상|중|하",
 "headline": "이번 주 핵심 판단 한 문장(한국어, 60자 내외)",
 "action": "온비가 이번 주 실행할 단 1가지(구체적, 한국어)"}"""


def synthesize(items, trend, model: str) -> dict:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key or not items:
        return {}
    client = Anthropic(api_key=key)
    lines = [f"- [{i.action}|{i.score}|{i.delta}|{i.bucket}] {i.title} → {i.so_what}"
             for i in sorted(items, key=lambda x: -x.score)]
    user = "■ 추세:\n" + " / ".join(trend) + "\n\n■ 이번 주 항목:\n" + "\n".join(lines)
    try:
        resp = client.messages.create(model=model, max_tokens=300, system=SYSTEM,
                                      messages=[{"role": "user", "content": user}])
        txt = "".join(b.text for b in resp.content if b.type == "text").strip()
        txt = txt.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(txt)
    except Exception as e:
        print(f"[editor] 실패: {e}")
        return {}
