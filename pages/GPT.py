import streamlit as st
from openai import OpenAI
import re

# OpenAI 객체 생성
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

def process_latex(text):
    """모든 LaTeX 수식을 처리하는 함수"""
    
    # 멀티라인 수식 처리 ($$...$$)
    text = re.sub(r'\$\$(.*?)\$\$', lambda m: f'$${m.group(1).strip()}$$', text, flags=re.DOTALL)
    
    # LaTeX 수식 문법 정규화
    text = text.replace('\\times', ' \\times ')  # 곱셈 기호 주변 공백 추가
    text = text.replace('\\pm', ' \\pm ')       # 플러스마이너스 기호 주변 공백 추가
    text = text.replace('\\neq', ' \\neq ')     # 부등호 주변 공백 추가
    
    # 단일 $ 처리
    text = re.sub(r'(?<![$])\$(?![$])(.*?)(?<![$])\$(?![$])', lambda m: f'${m.group(1).strip()}$', text)
    
    # 수식 내 여러 공백을 단일 공백으로 변경
    text = re.sub(r'\s+', ' ', text)
    
    return text

st.title("중1 수학 선생님 챗봇-성호중 범진")

# 메시지 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# KaTeX 스타일 추가
st.markdown("""
    <style>
        .katex { font-size: 1.1em; }
        .katex-display { overflow: auto hidden; }
    </style>
    """, unsafe_allow_html=True)

# 메시지 컨테이너 생성
message_container = st.container()

# 이전 메시지들 표시
with message_container:
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(process_latex(msg["content"]))

# 새로운 메시지가 있을 때 응답 생성
if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
    with st.chat_message("assistant"):
        response_container = st.empty()
        full_response = ""
        
        messages = st.session_state["messages"].copy()
        messages.insert(0, {
            "role": "system",
            "content": """당신은 중학교 1학년에게 수학 문제의 해결 방법을 차근차근 안내하는 교사입니다. 
            문제에 대해 곧바로 답을 알려주지 마세요. 당신은 문제를 대신 풀어주는 로봇이 아닙니다. 
            당신은 반드시 학생들이 풀이과정 중 오류가 있거나 이해가 안되는 부분이 있을 때 해당하는 부분을 문답법을 통해 알려줘야합니다. 
            챗봇을 활용하는 대상은 중학교 1학년 학생이기 때문에 한 번에 6문장을 넘게 전달하지 않고 차근차근 내용을 전달합니다. 중간중간 이해가 잘 되고 있는지 지속적으로 체크하세요.
            
            수식을 작성할 때는 반드시 LaTeX 문법을 사용하세요.
            1. 인라인 수식은 $...$ 로 표시
            2. 디스플레이 수식은 $$...$$ 로 표시
            3. 연산자 앞뒤로 적절한 공백을 넣어 가독성을 높이세요"""
        })
        
        stream = client.chat.completions.create(
            model="o1-mini-2024-09-12",
            messages=messages,
            stream=True
        )
        
        for response in stream:
            if response.choices[0].delta.content is not None:
                content = response.choices[0].delta.content
                full_response += content
                response_container.markdown(process_latex(full_response))
        
        st.session_state["messages"].append({"role": "assistant", "content": full_response})

# 채팅 입력
st.markdown("<div style='padding: 3rem;'></div>", unsafe_allow_html=True)
user_input = st.chat_input("선생님께 질문하세요...")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.rerun()
