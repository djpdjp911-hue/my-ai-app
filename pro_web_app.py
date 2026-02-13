import streamlit as st
import os
from PIL import Image
from google import genai
from google.genai import types

# -----------------------------------------------------------
# 1. 配置与身份认证 (已自动填入您的 API Key)
# -----------------------------------------------------------
#
my_api_key = "AIzaSyAuaxPpzujWcarcPUZoZKsNpaF810lco4M"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

st.set_page_config(page_title="杜佳鹏的万能实验室", layout="wide")
st.title("⚔️ 杜氏全栈 AI 助手")

# -----------------------------------------------------------
# 2. 初始化 AI 核心
# -----------------------------------------------------------
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=my_api_key)
    # 智能寻找可用模型
    models = [m.name for m in st.session_state.client.models.list() if "generateContent" in m.supported_actions]
    st.session_state.target_model = next((n for n in models if "flash" in n), models[0])

# -----------------------------------------------------------
# 3. 侧边栏：上传法宝 (图片)
# -----------------------------------------------------------
with st.sidebar:
    st.header("📸 识图专区")
    uploaded_file = st.file_uploader("上传一张图片让大侠看看...", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        st.image(uploaded_file, caption='已加载的法宝', use_container_width=True)

# -----------------------------------------------------------
# 4. 主界面：聊天窗口
# -----------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 处理用户输入
if prompt := st.chat_input("请少侠出招..."):
    # 用户输入展示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 响应处理
    with st.chat_message("assistant"):
        with st.spinner("大侠正在运功..."):
            # 准备内容列表
            contents = [f"你是一个武林大侠。请根据少侠杜佳鹏的要求回答。当前问题：{prompt}"]

            # 如果上传了图片，则加入内容
            if uploaded_file:
                img = Image.open(uploaded_file)
                contents.append(img)

            # 发送多模态请求
            response = st.session_state.client.models.generate_content(
                model=st.session_state.target_model,
                contents=contents
            )

            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})