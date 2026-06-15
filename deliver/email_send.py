"""주간 다이제스트 이메일 발송 (SMTP).
필요 환경변수: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, MAIL_TO
Gmail 예시: SMTP_HOST=smtp.gmail.com, SMTP_PORT=587, SMTP_PASS=앱비밀번호(2차인증 후 발급)
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send(html: str, subject: str):
    host, port = os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", "587"))
    user, pw, to = os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"), os.getenv("MAIL_TO")
    if not all([host, user, pw, to]):
        print("[email] SMTP 환경변수 부족 — 스킵")
        return
    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"], msg["To"] = user, to
    try:
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            s.login(user, pw)
            s.sendmail(user, [t.strip() for t in to.split(",")], msg.as_string())
        print(f"[email] 발송 완료 → {to}")
    except Exception as e:
        print(f"[email] 발송 실패: {e}")
