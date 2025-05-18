import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI

# === API 키 불러오기 ===
api_key = st.secrets["OPENAI_API_KEY"]

# === GPT 모델 초기화 ===
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.3,
    api_key=api_key  # 핵심: openai_api_key → api_key 로 수정
)

# === 엑셀 데이터 로드 ===
excel_path = "newsclip_db_updated.xlsx"
try:
    df = pd.read_excel(excel_path)
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error(f"❌ 엑셀 파일을 불러오는 중 오류 발생: {e}")
    st.stop()

# === 뉴스 요약 데이터 통합 ===
docs = []
for _, row in df.iterrows():
    if isinstance(row.get("뉴스요약"), str) and row["뉴스요약"].strip():
        date = str(row.get("날짜", ""))[:10]
        title = row.get("해드라인", "")
        summary = row["뉴스요약"].strip()
        docs.append(f"[{date}] {title} : {summary}")
context_text = "\n".join(docs)

# === Streamlit UI 설정 ===
st.set_page_config(page_title="뉴스 요약 GPT 챗봇", layout="wide")
st.title("📰 뉴스 요약 기반 GPT Q&A")
st.markdown("요약된 뉴스 내용을 기반으로 GPT에게 질문해보세요. **비상교육** 관련 기사라면 강조됩니다.")

# === 질문 입력 ===
question = st.text_input("질문을 입력하세요:", placeholder="예: 4월 AIDT 관련 주요 뉴스는?")

# === GPT 응답 처리 ===
if question:
    with st.spinner("GPT가 답변을 준비 중입니다..."):
        prompt = f"""
        아래는 뉴스 요약 내용입니다. 질문에 맞춰 관련 정보를 정리해서 답해주세요.
        비상교원 관련 기사라면 특별히 강조해주세요.

        질문: {question}

        뉴스 요약:
        {context_text}
        """
        try:
            response = llm.predict(prompt)
            st.markdown(
                f"""
                <div style='background-color: #f9f9f9; padding: 20px; border-radius: 12px;'>
                    <h4 style='color:#333;'>💬 질문</h4>
                    <p style='font-size:16px;'>{question}</p>
                    <hr style="margin-top: 20px; margin-bottom: 20px;">
                    <h4 style='color:#333;'>📘 GPT의 답변</h4>
                    <p style='font-size:16px; line-height:1.6;'>{response}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"❌ GPT 처리 중 오류 발생: {e}")
else:
    st.info("왼쪽 입력창에 질문을 입력해 주세요.")
