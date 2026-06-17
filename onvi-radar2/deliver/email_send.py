"""주간 다이제스트 이메일 발송 (SMTP) — 팀 다중 수신 + 첨부 지원.
필요 환경변수: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, MAIL_TO
- MAIL_TO: 쉼표로 여러 명 (예: a@x.com, b@x.com, c@x.com)
- Gmail 예시: SMTP_HOST=smtp.gmail.com, SMTP_PORT=587, SMTP_PASS=앱비밀번호
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header


def send(html: str, subject: str, attachments=None):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user, pw, to = os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"), os.getenv("MAIL_TO")
    if not all([host, user, pw, to]):
        print("[email] SMTP 환경변수 부족 — 스킵")
        return

    recipients = [t.strip() for t in to.split(",") if t.strip()]
    msg = MIMEMultipart()
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = user
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html", "utf-8"))

    # 첨부 (예: 피치 초안) — 파일 있을 때만
    for path in (attachments or []):
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(path))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(path)}"'
            msg.attach(part)

    try:
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            s.login(user, pw)
            s.sendmail(user, recipients, msg.as_string())
        print(f"[email] 발송 완료 → {len(recipients)}명: {', '.join(recipients)}")
    except Exception as e:
        print(f"[email] 발송 실패: {e}")
