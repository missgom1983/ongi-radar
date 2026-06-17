"""🎯 자동 산출물 엔진.
긴급검토·피치덱반영 항목으로 '피치덱 경쟁분석 슬라이드 초안'(markdown)을 생성.
복붙해서 바로 슬라이드로 쓸 수 있는 [제목/불릿/한 줄 메시지] 구조. 필요: ANTHROPIC_API_KEY
"""
import os
from anthropic import Anthropic

SYSTEM = """너는 온비의 투자자 피치덱을 만드는 전략 기획자다.
입력된 경쟁/근거 신호로 '경쟁 분석' 슬라이드 1~2장 초안을 만든다.
온비 포지셔닝: '케어 회사가 아니라 기억 회사'. 차별점: 자녀 결제·노인 수혜, 누적 음성/기억 자산 락인.
와플랫(B2G 안부전화 확산)·효돌(임상근거 보유)을 정면으로 다루되 온비 차별화로 마무리한다.
출력은 한국어 마크다운. 각 슬라이드는 다음 형식:
### [슬라이드 제목]
- 불릿 3~4개(사실 기반, 수치 포함)
> 한 줄 핵심 메시지
AI 티 나는 표현 금지, 투자자 보고 톤."""


def generate(items, model: str) -> str:
    key = os.getenv("ANTHROPIC_API_KEY")
    picks = [i for i in items if i.action in ("긴급검토", "피치덱반영")]
    if not key or not picks:
        return ""
    client = Anthropic(api_key=key)
    body = "\n".join(f"- [{i.bucket}] {i.title} → {i.so_what}" for i in picks)
    try:
        resp = client.messages.create(model=model, max_tokens=900, system=SYSTEM,
                                      messages=[{"role": "user", "content": body}])
        md = "".join(b.text for b in resp.content if b.type == "text").strip()
        with open("pitch_draft.md", "w", encoding="utf-8") as f:
            f.write(md)
        print("[pitch] pitch_draft.md 생성")
        return md
    except Exception as e:
        print(f"[pitch] 실패: {e}")
        return ""
