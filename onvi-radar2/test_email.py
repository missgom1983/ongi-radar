# -*- coding: utf-8 -*-
"""테스트 메일 1통 즉시 발송 — SMTP 연결만 확인. (뉴스/AI 키 불필요)"""
from collectors.base import Item
from digest.build import build_html
from deliver import email_send

items = [
    Item(source="news", title="[샘플] 와플랫 안부전화 전국 B2G 확장",
         url="https://example.com", published="2026-06-16",
         score=95, bucket="직접경쟁", action="긴급검토", delta="신규",
         so_what="이 메일이 보이면 자동 발송 준비 완료입니다 ✅"),
    Item(source="paper", title="[샘플] AI 회상치료가 온비 기억모듈을 뒷받침",
         url="https://example.com", published="2026-06-16",
         score=82, bucket="논문근거", action="피치덱반영", delta="신규",
         so_what="매주 월요일 9시, 이 형식으로 팀에 자동 발송됩니다"),
]
editor = {
    "threat": "중",
    "headline": "온비 레이더 테스트 발송 성공 🎉",
    "action": "이제 SMTP 연결이 확인됐습니다. 본 워크플로(월 9시)로 자동 발송하세요.",
}
html = build_html(items, editor=editor, trend=["📈 와플랫 가속 (1→2)"])
email_send.send(html, "[온비 레이더] 테스트 메일 ✅", attachments=None)
