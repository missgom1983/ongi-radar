# OnVi Radar — 온비 마켓 인텔리전스 에이전트

경쟁사 신호 + 시니어케어 논문을 매주 자동 수집 → Claude가 "온비 관점"으로 점수화 →
Notion 누적 저장 + 이메일 주간 브리프. **서버 불필요(GitHub Actions 무료 cron).**

```
수집(naver/g2b/papers) → 중복제거 → Claude 점수 → 60점 컷 → Notion 저장 → 이메일 발송
```

---

## 폴더 구조
```
onvi-radar/
├── config.yaml              # ★ 워치리스트·키워드·임계값 (여기만 수정)
├── main.py                  # 오케스트레이터
├── collectors/             # naver_news / g2b / papers (+ base)
├── pipeline/               # dedupe / score(Claude) / store_notion
├── digest/build.py         # 브랜드 토큰 HTML 다이제스트
├── deliver/email_send.py   # SMTP 발송
└── .github/workflows/weekly.yml   # 매주 월 08:00 KST 자동 실행
```

---

## 설치 (5단계)

### 1. 레포 올리기
GitHub에 새 비공개 레포 생성 → 이 폴더 전체 업로드(또는 `git push`).

### 2. API 키 발급
| 키 | 용도 | 발급처 | 필수 |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | 점수 엔진 | console.anthropic.com | ★필수 |
| `NAVER_CLIENT_ID` / `_SECRET` | 뉴스 | developers.naver.com (검색>뉴스) | 권장 |
| `DATA_GO_KR_KEY` | 나라장터 입찰 | data.go.kr (입찰공고정보서비스 신청) | 권장 |
| `NOTION_TOKEN` / `NOTION_DB_ID` | 저장 | notion.so/my-integrations | 선택 |
| `SMTP_*` / `MAIL_TO` | 이메일 | Gmail 앱비밀번호 등 | 선택 |

> 논문(OpenAlex·arXiv)은 키 불필요 — 바로 동작합니다.

### 3. GitHub Secrets 등록
레포 → Settings → Secrets and variables → Actions → New repository secret
위 표의 이름 그대로 등록.

### 4. Notion DB 준비 (저장 켤 경우)
빈 데이터베이스 생성 후 속성 추가:
`제목(Title) · 점수(Number) · 분류(Select) · So-What(Text) · 액션(Select) · 소스(Select) · 날짜(Date) · 링크(URL)`
→ DB 우상단 `...` > 연결 > 만든 통합 추가 → URL의 32자리를 `NOTION_DB_ID`로.

### 5. 첫 실행
Actions 탭 → `onvi-radar-weekly` → **Run workflow** (수동 실행)으로 테스트.
이후 매주 월요일 자동 발송.

### 로컬 테스트
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...   # 필요한 키 export
python main.py
```

---

## 튜닝
- **노이즈 많음** → `config.yaml`의 `score_threshold` 65~70으로 ↑
- **비용 절감** → `model: claude-haiku-4-5-20251001`
- **워치리스트 추가** → `competitors` / `category_keywords` 에 단어만 추가

---

## paper-downloader 연동
Radar는 논문 **메타데이터+요지만** 수집·점수화합니다.
브리프에서 중요 논문이 잡히면, 그 제목/키워드로 **paper-downloader 스킬**을 실행해
OA PDF 풀텍스트를 온디맨드로 받으세요. (같은 OpenAlex 소스라 중복 없이 맞물림)

---

## ⚠️ 법무 / 정보보호 (코드에 반영됨)
- 뉴스: **제목+링크+자체 요지만** 저장. 본문 전문 저장·재배포 금지(저작권).
- 논문: 초록은 요지로 재서술, **OA 링크만** 노출. 유료 논문 PDF 미수집.
- 크롤링 대신 **공식 OpenAPI 우선** 사용(이용약관·DB권 리스크 회피).
- Claude API에는 **공개 정보만** 투입. 내부 전략·고객 데이터 절대 미투입.
