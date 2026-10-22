import os
from datetime import datetime, timedelta, timezone

import requests
import streamlit as st
from dotenv import load_dotenv

# .env 파일에서 키를 읽어 옴 (키 값은 코드에 쓰지 않음)
load_dotenv()

API = {
    "geo": "https://api.openweathermap.org/geo/1.0/direct",       # 🔌 OpenWeather 지오코딩 (도시 → 위도·경도)
    "weather": "https://api.openweathermap.org/data/2.5/weather",  # 🔌 OpenWeather 현재 날씨
}

KST = timezone(timedelta(hours=9))


class WeatherError(Exception):
    """화면에 보여 줄 한국어 한 줄을 담는 에러 (주소·키는 담지 않음)."""


def call(url, params):
    """OpenWeather를 한 번 부름. 키가 주소에 들어가므로 주소·응답 객체는 밖으로 내보내지 않음."""
    params = {**params, "appid": os.getenv("OPENWEATHER_API_KEY")}
    try:
        res = requests.get(url, params=params, timeout=10)  # 🔌 API 호출
    except requests.RequestException:
        raise WeatherError("인터넷 연결을 확인해 주세요.")

    if res.status_code == 401:
        raise WeatherError("날씨 키가 틀렸거나 아직 켜지지 않았어요 (가입 후 최대 2시간).")
    if res.status_code == 404:
        raise WeatherError("그 도시를 찾지 못했어요.")
    if res.status_code == 429:
        raise WeatherError("1분에 너무 많이 불렀어요. 잠시 뒤에 다시 시도해 주세요.")
    if not res.ok:
        raise WeatherError(f"날씨 정보를 가져오지 못했어요. (HTTP {res.status_code})")
    return res.json()


@st.cache_data(ttl=600)  # 10분 동안은 저장해 둔 결과를 다시 씀 (에러는 저장되지 않음)
def fetch_weather(city):
    places = call(API["geo"], {"q": city, "limit": 1})
    if not places:
        raise WeatherError("그 도시를 찾지 못했어요. 영어 이름(예: Seoul)으로도 해 보세요.")
    place = places[0]
    lat, lon = place["lat"], place["lon"]                          # data[0]["lat"], ["lon"] = 위도·경도
    name = place.get("local_names", {}).get("ko", place["name"])  # data[0]["local_names"]["ko"] = 한국어 도시 이름

    data = call(API["weather"], {"lat": lat, "lon": lon, "units": "metric", "lang": "kr"})
    return {
        "name": name,
        "desc": data["weather"][0]["description"],  # data["weather"][0]["description"] = 날씨 설명
        "temp": data["main"]["temp"],               # data["main"]["temp"] = 지금 기온
        "feels": data["main"]["feels_like"],        # data["main"]["feels_like"] = 체감 온도
        "humidity": data["main"]["humidity"],       # data["main"]["humidity"] = 습도(%)
        "wind": data["wind"]["speed"],              # data["wind"]["speed"] = 풍속(m/s)
        "time": data["dt"],                         # data["dt"] = 관측 시각 (유닉스 시간)
    }


def outfit(temp):
    if temp >= 28: return "🩳 반팔·반바지"
    if temp >= 20: return "👕 얇은 긴팔"
    if temp >= 12: return "🧥 가벼운 겉옷"
    if temp >= 5: return "🧣 코트·니트"
    return "🧤 패딩·목도리"


STYLE = """
<style>
.stApp { background: linear-gradient(135deg, #E7F5FF 0%, #E6FCF5 40%, #FFF9DB 75%, #FFF0F6 100%); }
.title {
  font-size: 2.6rem; font-weight: 900; margin-bottom: 0;
  background: linear-gradient(90deg, #339AF0, #20C997, #FCC419, #FF922B, #F06595);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero {
  border-radius: 22px; padding: 18px 24px; margin: 8px 0 18px; color: #FFFFFF;
  background: linear-gradient(120deg, #339AF0, #22B8CF 55%, #20C997);
  box-shadow: 0 8px 22px rgba(51, 154, 240, 0.30);
}
.hero .city { font-size: 1.2rem; font-weight: 700; }
.hero .temp { font-size: 3rem; font-weight: 900; line-height: 1.1; }
.card {
  border-radius: 18px; padding: 14px 16px; color: #FFFFFF; margin-bottom: 14px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.10);
}
.card .head { font-size: 0.95rem; font-weight: 700; opacity: 0.95; }
.card .value { font-size: 1.5rem; font-weight: 900; margin-top: 4px; }
.note { color: #495057; font-size: 0.9rem; }
.apibox {
  border: 2px dashed #339AF0; border-radius: 14px; padding: 12px 16px;
  background: rgba(255, 255, 255, 0.7); color: #343A40; font-size: 0.9rem;
}
.apibox code { color: #D6336C; }
</style>
"""


st.set_page_config(page_title="오늘 날씨", page_icon="🌤️", layout="centered")
st.markdown(STYLE, unsafe_allow_html=True)
st.markdown('<p class="title">🌤️ 알록달록 오늘 날씨</p>', unsafe_allow_html=True)

if not os.getenv("OPENWEATHER_API_KEY"):
    st.error("`.env`에 OPENWEATHER_API_KEY가 없어요. `.env.example`을 보고 채워 주세요.")
    st.stop()

col_city, col_btn = st.columns([3, 1])
with col_city:
    city = st.text_input("도시", value="용인")
with col_btn:
    st.write("")
    if st.button("🔄 새로 불러오기"):
        st.cache_data.clear()

try:
    w = fetch_weather(city.strip())
except WeatherError as e:
    st.error(str(e))
    st.stop()

st.markdown(
    f'<div class="hero"><div class="city">📍 {w["name"]} · {w["desc"]}</div>'
    f'<div class="temp">{w["temp"]:.1f}°C</div>'
    f'<div>오늘 옷차림: {outfit(w["feels"])}</div></div>',
    unsafe_allow_html=True,
)

cards = [
    ("🌡️ 체감 온도", f'{w["feels"]:.1f}°C', "#FF922B"),
    ("💧 습도", f'{w["humidity"]}%', "#339AF0"),
    ("🍃 바람", f'{w["wind"]:.1f} m/s', "#20C997"),
]
for col, (head, value, color) in zip(st.columns(3), cards):
    with col:
        st.markdown(
            f'<div class="card" style="background:{color}">'
            f'<div class="head">{head}</div><div class="value">{value}</div></div>',
            unsafe_allow_html=True,
        )

observed = datetime.fromtimestamp(w["time"], KST).strftime("%Y-%m-%d %H:%M")
st.markdown(f'<p class="note">🕘 관측 시각: <b>{observed}</b> (한국 시간) · 결과는 10분 동안 저장해서 다시 써요.</p>',
            unsafe_allow_html=True)

# ── API 상자 (키를 뺀 기본 주소만) ──
st.markdown(
    f'<div class="apibox">🔌 <b>이 화면이 쓰는 API</b><br>'
    f'<code>{API["geo"]}</code><br><code>{API["weather"]}</code><br>'
    f'키가 주소에 들어가는 API라서 실제 요청 주소는 화면에 보여 주지 않아요.<br>'
    f'출처: 날씨 - OpenWeather</div>',
    unsafe_allow_html=True,
)
