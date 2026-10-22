import os
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

import requests
import streamlit as st
from dotenv import load_dotenv

# .env 파일에서 키를 읽어 옴 (키 값은 코드에 쓰지 않음)
load_dotenv()

API = {
    "rate": "https://v6.exchangerate-api.com/v6/latest/USD",  # 🔌 ExchangeRate-API 환율 (기준 통화 USD)
}

KST = timezone(timedelta(hours=9))

# 통화 코드: (이름, 국기, 보여 줄 단위, 카드 색)
CURRENCIES = {
    "USD": ("미국 달러", "🇺🇸", 1, "#FF6B6B"),
    "JPY": ("일본 엔", "🇯🇵", 100, "#FFA94D"),
    "EUR": ("유로", "🇪🇺", 1, "#51CF66"),
    "CNY": ("중국 위안", "🇨🇳", 1, "#339AF0"),
    "GBP": ("영국 파운드", "🇬🇧", 1, "#845EF7"),
    "VND": ("베트남 동", "🇻🇳", 1000, "#F06595"),
}

ERROR_MESSAGES = {
    "invalid-key": "환율 키가 틀렸어요. .env의 EXCHANGERATE_API_KEY를 확인해 주세요.",
    "inactive-account": "환율 사이트 가입 인증 메일을 확인해 주세요.",
    "quota-reached": "이번 달 무료 사용량(1,500번)을 다 썼어요.",
}


class RateError(Exception):
    """화면에 보여 줄 한국어 한 줄을 담는 에러 (주소·헤더는 담지 않음)."""


@st.cache_data(ttl=3600)  # 1시간 동안은 저장해 둔 결과를 다시 씀 (무료 월 1,500번)
def fetch_rates():
    """USD 기준 환율을 한 번 부름. 실패하면 RateError (에러는 캐시되지 않음)."""
    api_key = os.getenv("EXCHANGERATE_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}  # 키는 주소가 아니라 헤더로 보냄
    try:
        res = requests.get(API["rate"], headers=headers, timeout=10)  # 🔌 API 호출
        data = res.json()
    except requests.RequestException:
        raise RateError("인터넷 연결을 확인해 주세요.")
    except ValueError:
        raise RateError(f"환율 정보를 읽지 못했어요. (HTTP {res.status_code})")

    if data.get("result") != "success":  # data["result"] = "success" 또는 "error"
        error_type = data.get("error-type", "")  # data["error-type"] = 실패 이유
        raise RateError(ERROR_MESSAGES.get(error_type, f"환율 정보를 가져오지 못했어요. ({error_type or res.status_code})"))

    return {
        "rates": data["conversion_rates"],         # data["conversion_rates"] = 1달러가 각 통화로 얼마인지
        "updated": data["time_last_update_utc"],   # data["time_last_update_utc"] = 기준 시각 (UTC)
        "next": data["time_next_update_utc"],      # data["time_next_update_utc"] = 다음 갱신 시각 (UTC)
    }


def to_kst(utc_text):
    """'Fri, 27 Mar 2020 00:00:01 +0000' → '2020-03-27 09:00 (한국 시간)'"""
    return parsedate_to_datetime(utc_text).astimezone(KST).strftime("%Y-%m-%d %H:%M")


def krw_per(rates, code):
    """1 외화 = 몇 원. USD 기준 표라서 KRW 값 ÷ 그 통화 값."""
    return rates["KRW"] / rates[code]


def won(value):
    return f"{value:,.0f}원" if value >= 100 else f"{value:,.2f}원"


STYLE = """
<style>
.stApp {
  background: linear-gradient(135deg, #FFF0F6 0%, #FFF9DB 35%, #E6FCF5 70%, #E7F5FF 100%);
}
.title {
  font-size: 2.6rem; font-weight: 900; margin-bottom: 0;
  background: linear-gradient(90deg, #FF6B6B, #FFA94D, #FCC419, #51CF66, #339AF0, #845EF7);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.sub { color: #495057; margin-top: 0.2rem; }
.card {
  border-radius: 18px; padding: 16px 18px; color: #FFFFFF; margin-bottom: 14px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.10);
}
.card .head { font-size: 1rem; font-weight: 700; opacity: 0.95; }
.card .value { font-size: 1.6rem; font-weight: 900; margin-top: 4px; }
.result {
  border-radius: 22px; padding: 22px 26px; margin: 8px 0 18px;
  background: linear-gradient(120deg, #845EF7, #339AF0 55%, #20C997);
  color: #FFFFFF; box-shadow: 0 8px 22px rgba(51, 154, 240, 0.30);
}
.result .from { font-size: 1.1rem; opacity: 0.9; }
.result .to { font-size: 2.4rem; font-weight: 900; }
.note { color: #495057; font-size: 0.9rem; }
.apibox {
  border: 2px dashed #845EF7; border-radius: 14px; padding: 12px 16px;
  background: rgba(255, 255, 255, 0.7); color: #343A40; font-size: 0.9rem;
}
.apibox code { color: #D6336C; }
</style>
"""


st.set_page_config(page_title="환율 계산기", page_icon="💱", layout="centered")
st.markdown(STYLE, unsafe_allow_html=True)
st.markdown('<p class="title">💱 알록달록 환율 계산기</p>', unsafe_allow_html=True)
st.markdown('<p class="sub">금액과 통화를 고르면 원화로 바꿔 드려요.</p>', unsafe_allow_html=True)

if not os.getenv("EXCHANGERATE_API_KEY"):
    st.error("`.env`에 EXCHANGERATE_API_KEY가 없어요. `.env.example`을 보고 채워 주세요.")
    st.stop()

if st.button("🔄 새로 불러오기"):
    st.cache_data.clear()

try:
    info = fetch_rates()
except RateError as e:
    st.error(str(e))
    st.stop()

rates = info["rates"]

# ── 계산기 ──
direction = st.radio("어느 쪽으로 바꿀까요?", ["외화 → 원", "원 → 외화"], horizontal=True)
col_code, col_amount = st.columns([1, 1])
with col_code:
    code = st.selectbox(
        "통화",
        list(CURRENCIES),
        format_func=lambda c: f"{CURRENCIES[c][1]} {CURRENCIES[c][0]} ({c})",
    )
with col_amount:
    if direction == "외화 → 원":
        amount = st.number_input(f"금액 ({code})", min_value=0.0, value=100.0, step=10.0)
    else:
        amount = st.number_input("금액 (원)", min_value=0.0, value=100000.0, step=1000.0)

name, flag, _, _ = CURRENCIES[code]
if direction == "외화 → 원":
    result_from = f"{flag} {amount:,.2f} {code}"
    result_to = won(amount * krw_per(rates, code))
else:
    result_from = f"🇰🇷 {amount:,.0f}원"
    result_to = f"{amount / krw_per(rates, code):,.2f} {code}"

st.markdown(
    f'<div class="result"><div class="from">{result_from} =</div>'
    f'<div class="to">{result_to}</div></div>',
    unsafe_allow_html=True,
)

# ── 오늘의 환율 카드 ──
st.subheader("🌈 오늘의 기준 환율")
cols = st.columns(3)
for i, (c, (c_name, c_flag, unit, color)) in enumerate(CURRENCIES.items()):
    with cols[i % 3]:
        st.markdown(
            f'<div class="card" style="background:{color}">'
            f'<div class="head">{c_flag} {unit:,} {c_name}</div>'
            f'<div class="value">{won(unit * krw_per(rates, c))}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown(
    f'<p class="note">🕘 기준 시각: <b>{to_kst(info["updated"])}</b> (한국 시간) · '
    f'다음 갱신: {to_kst(info["next"])} · 하루 한 번 발표되는 기준값이에요.</p>',
    unsafe_allow_html=True,
)

# ── API 상자 (키를 뺀 기본 주소만) ──
st.markdown(
    f'<div class="apibox">🔌 <b>이 화면이 쓰는 API</b><br>'
    f'<code>{API["rate"]}</code><br>'
    f'키는 주소가 아니라 <code>Authorization</code> 헤더로 보내요. 결과는 1시간 동안 저장해서 다시 써요.<br>'
    f'출처: 환율 - ExchangeRate-API</div>',
    unsafe_allow_html=True,
)
