import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import RetrievalQA

# Load env
load_dotenv("C:\\Users\\shaik\\OneDrive\\Desktop\\rag\\.env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise Exception("Missing GEMINI_API_KEY in .env")

os.environ.setdefault(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
)

# Flask app
app = Flask(__name__)
CORS(app)

# Build QA chain
def build_qa_chain():

    loader = WebBaseLoader(
        "https://www.geeksforgeeks.org/python/"
    )

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    splits = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(
        splits,
        embeddings
    )

    retriever = vectorstore.as_retriever()

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=API_KEY
    )

    prompt = PromptTemplate.from_template("""
You are an expert assistant.
Use ONLY the provided context to answer the question.

Context:
{context}

Question:
{question}

Answer:
""")

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False
    )

    return qa_chain

qa_chain = build_qa_chain()

# API route
@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    question = data.get("question")

    response = qa_chain.invoke({
        "query": question
    })

    return jsonify({
        "answer": response["result"]
    })

# Run server
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)