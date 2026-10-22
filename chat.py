import os

import openai
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 키를 읽어 옴 (키 값은 코드에 쓰지 않음)
load_dotenv()

API = {
    "chat": "https://api.openai.com/v1",  # 🔌 OpenAI Chat Completions (모델 gpt-4o-mini)
}

MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = "너는 친절한 한국어 도우미야. 짧고 쉽게 대답해."

# 에러 메시지에는 키 일부가 섞여 올 수 있어서, 원문 대신 한국어 한 줄만 보여 줌
ERROR_MESSAGES = {
    openai.AuthenticationError: "OpenAI 키가 틀렸어요. .env의 OPENAI_API_KEY를 확인해 주세요.",
    openai.PermissionDeniedError: "이 키로는 gpt-4o-mini를 쓸 수 없어요. OpenAI 계정 권한을 확인해 주세요.",
    openai.RateLimitError: "사용량 한도를 넘었거나 크레딧이 없어요. OpenAI 결제 화면을 확인해 주세요.",
    openai.APITimeoutError: "응답이 너무 늦어요. 잠시 뒤 다시 보내 주세요.",  # 연결 오류의 한 종류라 먼저 검사
    openai.APIConnectionError: "인터넷 연결을 확인해 주세요.",
}


def korean_error(e):
    for error_type, message in ERROR_MESSAGES.items():
        if isinstance(e, error_type):
            return message
    if isinstance(e, openai.APIStatusError):
        return f"OpenAI가 대답하지 못했어요. (HTTP {e.status_code})"
    return "대답을 받지 못했어요. 잠시 뒤 다시 보내 주세요."


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
.apibox {
  border: 2px dashed #845EF7; border-radius: 14px; padding: 12px 16px;
  background: rgba(255, 255, 255, 0.7); color: #343A40; font-size: 0.9rem;
}
.apibox code { color: #D6336C; }
</style>
"""


st.set_page_config(page_title="챗봇", page_icon="💬", layout="centered")
st.markdown(STYLE, unsafe_allow_html=True)
st.markdown('<p class="title">💬 알록달록 챗봇</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub">무엇이든 물어보세요. ({MODEL})</p>', unsafe_allow_html=True)

if not os.getenv("OPENAI_API_KEY"):
    st.error("`.env`에 OPENAI_API_KEY가 없어요. `.env.example`을 보고 채워 주세요.")
    st.stop()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=API["chat"], timeout=30)

# 대화 기록은 브라우저 탭마다 따로 저장됨
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("🧹 대화 지우기"):
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(  # 🔌 API 호출
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                stream=True,
            )
            answer = st.write_stream(stream)  # 글자가 오는 대로 바로 보여 줌
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except openai.OpenAIError as e:
            st.session_state.messages.pop()  # 실패한 질문은 기록에서 빼서 다시 보낼 수 있게
            st.error(korean_error(e))

# ── API 상자 (키를 뺀 기본 주소만) ──
st.markdown(
    f'<div class="apibox">🔌 <b>이 화면이 쓰는 API</b><br>'
    f'<code>{API["chat"]}/chat/completions</code> · 모델 <code>{MODEL}</code><br>'
    f'키는 주소가 아니라 <code>Authorization</code> 헤더로 보내요. 질문할 때마다 사용 요금이 나가요.<br>'
    f'출처: 대답 - OpenAI</div>',
    unsafe_allow_html=True,
)
