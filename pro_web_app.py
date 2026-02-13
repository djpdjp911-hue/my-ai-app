import streamlit as st
import os
from PIL import Image
from google import genai
from google.genai import types

# -----------------------------------------------------------
# 1. 身份认证 (杜佳鹏专用)
# -----------------------------------------------------------
if "GEMINI_API_KEY" in st.secrets:
    my_api_key = st.secrets["GEMINI_API_KEY"]


st.set_page_config(page_title="杜佳鹏的万能实验室", layout="wide")
st.title("⚔️ 杜氏全栈 AI 助手")

# -----------------------------------------------------------
# 2. 初始化 AI 核心
# -----------------------------------------------------------
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=my_api_key)
    models = [m.name for m in st.session_state.client.models.list() if "generateContent" in m.supported_actions]
    st.session_state.target_model = next((n for n in models if "flash" in n), models[0])

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------
# 3. 侧边栏：性格/识图/重置
# -----------------------------------------------------------
with st.sidebar:
    st.header("🎭 灵魂注入")
    # 🌟 新增：性格选择下拉框
    personality_type = st.selectbox(
        "请选择大侠的灵魂：",
        ["武林大侠", "毒舌码农", "温柔老师"]
    )
    
    # 定义不同性格的指令
    personalities = {
        "武林大侠": "你是一个隐居深山的武林大侠，称呼用户为少侠。说话要有古风，带点江湖气息。",
        "毒舌码农": "你是一个工作了10年的资深程序员，说话非常刻薄、爱吐槽，喜欢用代码术语开玩笑，对小白问题很没耐心。",
        "温柔老师": "你是一个非常有耐心的幼儿园老师，说话温柔，喜欢用鼓励的语气，会把复杂的知识讲得非常简单易懂。"
    }
    
    current_instruction = personalities[personality_type]
    
    st.divider()
    st.header("📸 识图专区")
    uploaded_file = st.file_uploader("上传一张图片...", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    if st.button("🧼 重置记忆 (洗髓经)"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------------------------------------
# 4. 主界面：对话逻辑
# -----------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("请少侠出招..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"{personality_type}正在思考..."):
            contents = [f"请根据少侠杜佳鹏的要求回答。当前问题：{prompt}"]
            if uploaded_file:
                img = Image.open(uploaded_file)
                contents.append(img)
            
            # 🌟 关键：将当前选中的性格指令传入
            response = st.session_state.client.models.generate_content(
                model=st.session_state.target_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=current_instruction # 动态切换灵魂
                )
            )
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})


