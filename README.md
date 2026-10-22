# D7 · 파이썬으로 API 키 지키기

어제(D6)는 **브라우저(HTML)** 가 키 없는 API를 불렀고, 오늘(D7)은 **파이썬** 이 키가 필요한 오픈API를 불렀다.
키는 `.env` 금고에 넣고, 코드에는 이름만 쓴다.

## 오늘 만든 것

| 파일 | 하는 일 | 화면 | 실행 |
| --- | --- | --- | --- |
| `lotto.py` | 버튼을 누르면 로또 번호 6개 × 5세트, 공 색상·날짜 표시 | tkinter 창 | `python lotto.py` |
| `weather.py` | 도시를 입력하면 기온·체감 온도·습도·바람·날씨 설명 + 옷차림 추천, 알록달록 카드 (OpenWeather, 기본 도시 용인) | Streamlit 웹 | `streamlit run weather.py` |
| `rateCalc.py` | 외화 ↔ 원 환율 계산기 + 오늘의 기준 환율 카드 6개 (ExchangeRate-API) | Streamlit 웹 | `streamlit run rateCalc.py` |

> ⚠️ Streamlit 파일을 `python 파일.py` 로 실행하면 화면이 안 뜬다. 반대로 `print` 로 만든 파일을 `streamlit run` 으로 열면 화면은 비고 결과는 터미널에만 나온다.

## 처음 준비

```bash
# 1. 가상환경 (버전 통일)
conda create -n camp python=3.12 -y
conda activate camp

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 키 금고 만들기: .env.example 을 복사해 .env 로 이름을 바꾸고 = 뒤에 내 키를 채운다
```

`.env` 모양 (띄어쓰기·따옴표 없이):

```
OPENWEATHER_API_KEY=
EXCHANGERATE_API_KEY=
```

| 키 | 받는 곳 | 메모 |
| --- | --- | --- |
| `OPENWEATHER_API_KEY` | https://openweathermap.org/ | 가입 후 키가 켜지는 데 최대 2시간 |
| `EXCHANGERATE_API_KEY` | https://www.exchangerate-api.com/ | 가입 인증 메일 확인 필요, 무료 월 1,500번 |

## 배운 것

### 1. 키는 금고(`.env`)에, 코드엔 이름만
- 코드: `os.getenv("OPENWEATHER_API_KEY")` — 키 값은 코드·주석·README 어디에도 쓰지 않는다.
- `.gitignore` 에 `.env` 를 넣어 GitHub에 올라가지 않게 한다. `.env.example` 에는 **이름만** 적어 올린다.
- 키가 없으면 "`.env`에 ○○_API_KEY가 없어요" 라고 한국어로 알려 준다.

### 2. 키를 보내는 두 가지 방법
| API | 키 위치 | 주의 |
| --- | --- | --- |
| OpenWeather | 주소 안 `appid=키` | 요청 주소·`response.url` 을 출력하면 키가 그대로 보인다 |
| ExchangeRate-API | 헤더 `Authorization: Bearer 키` | 주소(`/v6/키/latest/USD`)에 넣지 않는다 |

그래서 화면·터미널에는 **키를 뺀 기본 주소만** 보여 준다.

### 3. 실패해도 한국어 한 줄
영어 에러 덩어리(Traceback) 대신 다음 행동을 알려 준다.

| 상황 | 안내 |
| --- | --- |
| OpenWeather 401 | 날씨 키가 틀렸거나 아직 켜지지 않았어요 (가입 후 최대 2시간) |
| OpenWeather 404 / 429 | 그 도시를 찾지 못했어요 / 1분에 너무 많이 불렀어요 |
| ExchangeRate `invalid-key` | 환율 키가 틀렸어요 |
| ExchangeRate `inactive-account` | 환율 사이트 가입 인증 메일을 확인해 주세요 |
| ExchangeRate `quota-reached` | 이번 달 무료 사용량(1,500번)을 다 썼어요 |

### 4. Streamlit은 클릭할 때마다 처음부터 다시 실행된다 → 캐시
- API 함수에 `@st.cache_data(ttl=초)` — 날씨 600초, 환율 3600초.
- "🔄 새로 불러오기" 버튼에서만 `st.cache_data.clear()`.
- 캐시가 없으면 통화를 바꿀 때마다 API를 불러 무료 사용량이 금방 바닥난다.

### 5. 환율은 "실시간"이 아니다
무료 환율은 하루 한 번 발표되는 기준값이다. 응답의 `time_last_update_utc` 를 **한국 시간**으로 바꿔 "기준 시각"으로 보여 주고, "실시간"이라고 쓰지 않는다.

### 6. 터미널 vs Streamlit
| | 터미널 | Streamlit |
| --- | --- | --- |
| 실행 | `python 파일.py` | `streamlit run 파일.py` |
| 출력 | `print()` | `st.write`, `st.metric`, `st.error` … |
| 입력 | `input()` | `st.text_input`, `st.selectbox`, `st.button` |

Streamlit 배경이 까맣게 나오면 Windows 다크 모드를 따라간 것이다. `.streamlit/config.toml` 에 `base = "light"` 로 밝은 테마를 고정했다.

## 폴더 구조

실행하는 코드는 맨 위에, 읽는 자료는 폴더 안에 둔다. 그래서 실행 명령이 `python 파일.py` 한 줄로 끝난다.

```
D07-python/
├─ lotto.py                  # 로또 (tkinter)
├─ weather.py                # 날씨 (Streamlit)
├─ rateCalc.py               # 환율 계산기 (Streamlit)
├─ requirements.txt          # pip install -r requirements.txt
├─ README.md                 # 지금 이 파일
├─ CLAUDE.md                 # 이 폴더에서 Claude Code가 지킬 규칙
├─ .env.example              # 필요한 키 이름 (값은 비움)
├─ .env                      # 내 키 (GitHub에 안 올라감)
│
├─ prompts/                  # 내가 Claude Code에게 보낸 요청 메모
│  ├─ 01_lotto.md
│  ├─ 02_weather.md
│  └─ 03_rateCalc.md
│
├─ docs/                     # D7 수업 자료 (받은 그대로)
│  ├─ 00_시작하기.md ~ 07_파이썬_실행방법_터미널_스트림릿.md
│  ├─ CLAUDE_파이썬API규칙.md  # CLAUDE.md 원본 규칙
│  ├─ CLAUDE_하루3번규칙.md
│  └─ D07_1022.html          # 워크북
│
├─ .streamlit/config.toml    # 밝은 테마 고정
├─ .vscode/settings.json     # VS Code가 conda 사용
└─ .claude/                  # 규칙(rules) · 검사 스킬(/api-check)
```

| 새 파일을 만들 때 | 어디에 |
| --- | --- |
| 실행하는 `.py` | 맨 위 (`streamlit run`은 맨 위의 `.streamlit/config.toml`을 읽음) |
| Claude Code에게 보낼 요청 메모 | `prompts/` 에 `04_이름.md` 처럼 번호를 붙여서 |
| 수업에서 받은 자료 | `docs/` |

## 커밋 전 확인
- [ ] `git status` 에 `.env` 가 안 보인다
- [ ] 내 키 앞 6글자로 검색 → `.env` 말고 0건
- [ ] `.env.example` 의 `=` 뒤가 모두 빈칸

## 데이터 출처
- 날씨: [OpenWeather](https://openweathermap.org/)
- 환율: [ExchangeRate-API](https://www.exchangerate-api.com/)
