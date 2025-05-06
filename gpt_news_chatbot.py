import os
import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI

# 1. 환경 변수에서 API 키 불러오기
api_key = st.secrets["OPENAI_API_KEY"]

# 2. 엑셀 데이터 불러오기
excel_path = "newsclip_db_updated.xlsx"
df = pd.read_excel(excel_path)
df.columns = df.columns.str.strip()  # 공백 제거

# 컬럼 확인 (디버깅용, 문제 해결 후 주석 처리 가능)
# st.write(df.columns.tolist())

# 3. 뉴스 요약 텍스트를 하나의 context로 통합
docs = []
for _, row in df.iterrows():
    if isinstance(row.get("뉴스요약"), str) and row["뉴스요약"].strip():
        date = str(row.get("날짜", ""))[:10]
        title = row.get("해드라인", "")
        summary = row["뉴스요약"].strip()
        docs.append(f"[{date}] {title} : {summary}")

context_text = "\n".join(docs)

# 4. GPT 모델 준비
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.3,
    openai_api_key=api_key
)

# 5. Streamlit 인터페이스
st.set_page_config(page_title="뉴스 요약 GPT 챗봇", layout="wide")
st.title("📰 뉴스 요약 기반 경영진 질의응답 GPT")

question = st.text_input("질문을 입력하세요:", placeholder="예: 4월 교육정책 요약해줘")

if question:
    with st.spinner("GPT가 답변을 준비 중입니다..."):
        prompt = f"""
        아래는 뉴스 요약 데이터입니다. 사용자의 질문에 맞는 내용을 정리해서 답변해 주세요. 
        특히 비상교육이 중심이 되는 기사가 있다면 그 내용을 강조해 주세요.

        질문: {question}

        뉴스 요약:
        {context_text}
        """
        try:
            response = llm.predict(prompt)
            st.success("답변 결과:")
            st.markdown(response)
        except Exception as e:
            st.error(f"오류 발생: {e}")
