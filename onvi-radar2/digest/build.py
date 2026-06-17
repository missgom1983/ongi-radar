"""점수 통과 항목으로 주간 HTML 다이제스트 생성. 온비 브랜드 토큰 적용."""
from datetime import date

# 온비 브랜드 토큰
HANJI, CHEONGJA, SIMHAE, SIMYA, NOEUL = "#F5F1E6", "#4FB89E", "#2C4A6B", "#1F2A3A", "#D9B88C"
ANGAE = "#C8E5DB"
ACTION_COLOR = {"긴급검토": "#C0392B", "피치덱반영": CHEONGJA, "모니터링": SIMHAE, "무시": "#999"}
BUCKET_ORDER = ["직접경쟁", "지원사업", "규제·법무", "인접", "카테고리신호", "논문근거"]


def build_html(items, editor=None, trend=None) -> str:
    items = sorted([i for i in items], key=lambda x: (-x.score))
    by_bucket = {}
    for it in items:
        by_bucket.setdefault(it.bucket or "기타", []).append(it)

    # ── ✍️ 에디터 종합 블록 ──
    editor = editor or {}
    editor_html = ""
    if editor.get("headline"):
        thr = editor.get("threat", "중")
        thr_color = {"상": "#C0392B", "중": NOEUL, "하": SIMHAE}.get(thr, NOEUL)
        editor_html = f"""
        <div style="background:{SIMYA};color:{HANJI};padding:16px 18px;border-radius:10px;margin-bottom:14px;">
          <div style="font-size:12px;color:{CHEONGJA};font-weight:700;">✍️ 이번 주 종합 · 위협도
            <span style="background:{thr_color};color:#fff;padding:1px 8px;border-radius:10px;">{thr}</span></div>
          <div style="font-size:16px;font-weight:700;margin:6px 0;">{editor['headline']}</div>
          <div style="font-size:13px;color:{NOEUL};">🎯 이번 주 할 일: {editor.get('action','')}</div>
        </div>"""

    # ── 📈 추세 칩 ──
    trend_html = ""
    if trend:
        chips = "".join(f'<span style="background:{ANGAE};color:{SIMHAE};padding:3px 10px;'
                        f'border-radius:12px;font-size:12px;margin:2px;display:inline-block;">{t}</span>'
                        for t in trend)
        trend_html = f'<div style="margin-bottom:14px;">{chips}</div>'

    rows = []
    for b in BUCKET_ORDER + [k for k in by_bucket if k not in BUCKET_ORDER]:
        if b not in by_bucket:
            continue
        rows.append(f'<h3 style="color:{SIMHAE};border-bottom:2px solid {CHEONGJA};'
                    f'padding-bottom:4px;margin:24px 0 8px;">{b} ({len(by_bucket[b])})</h3>')
        for it in by_bucket[b]:
            ac = ACTION_COLOR.get(it.action, "#999")
            badge = ('<span style="background:#C0392B;color:#fff;font-size:10px;'
                     'padding:1px 6px;border-radius:8px;margin-left:6px;">NEW</span>'
                     if it.delta == "신규" else
                     '<span style="background:#ccc;color:#555;font-size:10px;'
                     'padding:1px 6px;border-radius:8px;margin-left:6px;">지속</span>')
            rows.append(f"""
            <div style="margin:10px 0;padding:12px 14px;background:#fff;border-radius:8px;
                        border-left:4px solid {ac};">
              <div style="font-size:12px;color:{ac};font-weight:700;">{it.action} · {it.score}점 · {it.source}{badge}</div>
              <a href="{it.url}" style="color:{SIMYA};font-weight:600;text-decoration:none;font-size:15px;">{it.title}</a>
              <div style="color:{SIMHAE};font-size:13px;margin-top:4px;">→ {it.so_what}</div>
            </div>""")

    urgent = [i for i in items if i.action == "긴급검토"]
    banner = ""
    if urgent:
        banner = (f'<div style="background:{NOEUL};color:{SIMYA};padding:10px 14px;'
                  f'border-radius:8px;margin-bottom:16px;font-weight:700;">'
                  f'⚠ 긴급검토 {len(urgent)}건 — 즉시 확인 필요</div>')

    return f"""<!doctype html><html><body style="margin:0;background:{HANJI};
      font-family:Pretendard,-apple-system,sans-serif;padding:24px;">
      <div style="max-width:640px;margin:0 auto;">
        <div style="color:{CHEONGJA};font-weight:800;font-size:22px;">온비 레이더 · 주간 브리프</div>
        <div style="color:{SIMHAE};font-size:13px;margin-bottom:16px;">{date.today()} · 총 {len(items)}건</div>
        {editor_html}{trend_html}{banner}{''.join(rows)}
        <div style="color:#999;font-size:11px;margin-top:24px;">
          OnVi Radar · 자동 수집·점수화 결과입니다. 풀 PDF는 paper-downloader로 온디맨드 수집하세요.</div>
      </div></body></html>"""
