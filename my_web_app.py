import streamlit as st
import os
from google import genai

# -----------------------------------------------------------
# 1. 基础配置 (自动填充少侠的秘钥)
# -----------------------------------------------------------
my_api_key = "AIzaSyAuaxPpzujWcarcPUZoZKsNpaF810lco4M"  #
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 网页标题和图标
st.set_page_config(page_title="杜佳鹏的江湖实验室", page_icon="⚔️")
st.title("⚔️ 杜氏 AI 网页助手")
st.caption("基于 Gemini 2.0/1.5 Flash 构建的网页应用")

# -----------------------------------------------------------
# 2. 初始化 AI 客户端
# -----------------------------------------------------------
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=my_api_key)
    # 自动寻找可用模型
    models = [m.name for m in st.session_state.client.models.list() if "generateContent" in m.supported_actions]
    st.session_state.target_model = next((n for n in models if "flash" in n), models[0])

# 3. 初始化聊天记忆
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------
# 4. 网页布局：展示对话历史
# -----------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------------
# 5. 用户输入与响应
# -----------------------------------------------------------
if prompt := st.chat_input("少侠，想聊点什么？"):
    # 展示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 展示 AI 响应
    with st.chat_message("assistant"):
        response_placeholder = st.empty()  # 创建占位符实现打字机效果
        full_response = ""

        # 发送请求
        response = st.session_state.client.models.generate_content(
            model=st.session_state.target_model,
            contents=prompt,
            config={'system_instruction': "你是一个武林大侠，现在在网页上为少侠杜佳鹏服务。"}
        )

        full_response = response.text
        response_placeholder.markdown(full_response)

    # 存入记忆
    st.session_state.messages.append({"role": "assistant", "content": full_response})