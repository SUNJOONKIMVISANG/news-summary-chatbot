import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# 1. 환경 변수 불러오기
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 2. LLM 객체 생성
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.3,
    api_key=api_key
)

# 3. 뉴스 요약 데이터 불러오기
df = pd.read_excel("newsclip_db_updated.xlsx")  # 리포에 포함된 상대 경로 파일

# 4. Streamlit UI
st.set_page_config(page_title="뉴스 요약 기반 GPT", page_icon="📰")
st.title("📰 뉴스 요약 기반 경영진 질의응답 GPT")
user_input = st.text_input("질문을 입력하세요:", placeholder="예: 4월 교육정책 요약해줘")

if user_input:
    with st.spinner("답변 생성 중..."):
        context = "\n".join(df["요약"].astype(str).tolist())
        message = f"다음은 뉴스 요약입니다:\n{context}\n\n{user_input}에 대한 답을 제공해줘."
        response = llm([HumanMessage(content=message)])
        st.success(response.content)
