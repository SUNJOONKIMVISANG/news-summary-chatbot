import os
import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
api_key = st.secrets["OPENAI_API_KEY"]

# GPT 및 임베딩 모델
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3, openai_api_key=api_key)
embedding_model = OpenAIEmbeddings(openai_api_key=api_key)

# 데이터 로딩
excel_path = "newsclip_db_updated.xlsx"
df = pd.read_excel(excel_path)
df.columns = df.columns.str.strip()

# 벡터 DB 초기화
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
documents = []

# 뉴스 요약 -> Document 리스트 변환
for _, row in df.iterrows():
    if isinstance(row.get("뉴스요약"), str) and row["뉴스요약"].strip():
        date = str(row.get("날짜", ""))[:10]
        title = row.get("해드라인", "")
        summary = row["뉴스요약"].strip()
        content = f"[{date}] {title} : {summary}"
        doc = Document(page_content=content, metadata={"title": title, "date": date})
        documents.append(doc)

# 문서 분할 및 벡터화
split_docs = text_splitter.split_documents(documents)
vectordb = Chroma.from_documents(split_docs, embedding_model, persist_directory="chromadb")

# Streamlit 설정
st.set_page_config(page_title="뉴스 요약 GPT 챗봇", layout="wide")
st.title("📰 뉴스 요약 기반 RAG 질의응답 GPT")

# 질문 입력
question = st.text_input("질문을 입력하세요:", placeholder="예: 4월 AIDT 관련 주요 뉴스는?")

# 질문 처리
if question:
    with st.spinner("GPT가 답변을 준비 중입니다..."):
        # RAG: 유사 문서 검색
        top_docs = vectordb.similarity_search(question, k=5)
        context = "\n".join([doc.page_content for doc in top_docs])

        # GPT 프롬프트 구성
        prompt = f"""
        아래는 뉴스 요약 내용입니다. 질문에 답해주세요. 특히 비상교육 관련 기사가 있다면 강조해주세요.

        질문: {question}

        뉴스 요약:
        {context}
        """

        try:
            response = llm.predict(prompt)
            st.markdown(
                f"""
                <div style='background-color: #f9f9f9; padding: 20px; border-radius: 12px;'>
                    <h4 style='color:#333;'>💬 질문</h4>
                    <p style='font-size:16px;'>{question}</p>
                    <hr style="margin-top: 20px; margin-bottom: 20px;">
                    <h4 style='color:#333;'>📘 답변</h4>
                    <p style='font-size:16px; line-height:1.6;'>{response}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
