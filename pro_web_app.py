import streamlit as st
import os
from PIL import Image
from google import genai
from google.genai import types
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# -----------------------------------------------------------
# 1. 身份认证 (杜佳鹏专用)
# -----------------------------------------------------------
#
my_api_key = "AIzaSyAuaxPpzujWcarcPUZoZKsNpaF810lco4M"

if "GEMINI_API_KEY" in st.secrets:
    my_api_key = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title="杜佳鹏的万能实验室", layout="wide")
st.title("⚔️ 杜氏全栈 AI 助手 (联网增强版)")

# -----------------------------------------------------------
# 2. 初始化 AI 核心
# -----------------------------------------------------------
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=my_api_key)
    #
    models = [m.name for m in st.session_state.client.models.list() if "generateContent" in m.supported_actions]
    st.session_state.target_model = next((n for n in models if "flash" in n), models[0])

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------
# 3. 侧边栏配置
# -----------------------------------------------------------
with st.sidebar:
    st.header("🎭 灵魂注入")
    personality_type = st.selectbox("选择灵魂：", ["武林大侠", "毒舌码农", "温柔老师"])
    personalities = {
        "武林大侠": "你是一个隐居武林大侠，称呼用户为少侠。你可以通过‘千里传音’（联网）查询江湖最新动态。",
        "毒舌码农": "你是一个资深程序员。如果遇到不懂的新技术，你会偷偷百度一下再回来吐槽。",
        "温柔老师": "你是一个温柔的老师，会帮小朋友查查今天的天气和有趣的新闻。"
    }
    current_instruction = personalities[personality_type]

    st.divider()
    # 🌟 新增：联网搜索开关
    enable_search = st.toggle("开启实时联网搜索", value=True)
    enable_voice = st.toggle("开启语音播报", value=True)

    st.divider()
    st.header("🎤 语音输入")
    audio_input = mic_recorder(start_prompt="开始说话", stop_prompt="结束并发送", key='recorder')

    st.divider()
    st.header("📸 识图专区")
    uploaded_file = st.file_uploader("上传图片...", type=['png', 'jpg', 'jpeg'])

    if st.button("🧼 重置记忆 (洗髓经)"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------------------------------------
# 4. 主界面逻辑
# -----------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

user_prompt = st.chat_input("请少侠出招...")
active_prompt = user_prompt
audio_bytes = audio_input['bytes'] if audio_input else None

if audio_input:
    active_prompt = "这是我的语音指令"

if active_prompt:
    st.session_state.messages.append({"role": "user", "content": active_prompt})
    with st.chat_message("user"):
        st.markdown(active_prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"{personality_type}正在查阅江湖情报..."):
            contents = [f"请根据少侠杜佳鹏的要求回答。当前问题：{active_prompt}"]
            if uploaded_file:
                contents.append(Image.open(uploaded_file))
            if audio_bytes:
                contents.append(types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"))

            # 🌟 核心：配置联网工具
            tools = []
            if enable_search:
                tools.append(types.Tool(
                    google_search=types.GoogleSearchRetrieval(
                        dynamic_retrieval_config=types.DynamicRetrievalConfig(
                            mode="unspecified",
                            dynamic_threshold=0.06  # 触发搜索的敏感度
                        )
                    )
                ))

            response = st.session_state.client.models.generate_content(
                model=st.session_state.target_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=current_instruction,
                    tools=tools  # 注入工具
                )
            )

            reply_text = response.text
            st.markdown(reply_text)

            # 自动展示搜索来源 (如果有)
            if response.candidates[0].grounding_metadata:
                with st.expander("🌐 查看搜索来源"):
                    st.json(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)

            msg_data = {"role": "assistant", "content": reply_text}

            if enable_voice:
                tts = gTTS(text=reply_text, lang='zh-cn')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format="audio/mp3")
                msg_data["audio"] = audio_fp

            st.session_state.messages.append(msg_data)
