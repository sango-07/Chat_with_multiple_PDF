import streamlit as st
from dotenv import load_dotenv
import os
from htmlTemplate import css, bot_template, user_template
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.spacy_embeddings import SpacyEmbeddings
from langchain_community.llms import LlamaCpp
from langchain.embeddings import HuggingFaceEmbeddings 
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer, util
from langchain_openai import AzureOpenAIEmbeddings
import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_openai import ChatOpenAI
os.environ["GROQ_API_KEY"]=os.getenv('GROQ_API_KEY')
from langchain_groq import ChatGroq

llmtemplate = """You’re an AI information specialist with a strong emphasis on extracting accurate information from markdown documents. Your expertise involves summarizing data succinctly while adhering to strict guidelines about neutrality and clarity.

Your task is to answer a specific question based on a provided markdown document. Here is the question you need to address:  
{question}

Keep in mind the following instructions:  
- Your response should be direct and factual, limited to 50 words and 2-3 sentences.  
- Avoid using introductory phrases like "yes" or "no."  
- Maintain an ethical and unbiased tone, steering clear of harmful or offensive content.  
- If the document lacks relevant information, respond with "I cannot provide an answer based on the provided document."  
- Do not fabricate information, include questions, or use confirmatory phrases.  
- Remember not to prompt for additional information or ask any questions.  

Ensure your response is strictly based on the content of the markdown document.
    """



def prepare_docs(pdf_docs):
    docs = []
    metadata = []
    content = []

    for pdf in pdf_docs:
        print(pdf.name)
        pdf_reader = PyPDF2.PdfReader(pdf)
        for index, text in enumerate(pdf_reader.pages):
            doc_page = {'title': pdf.name + " page " + str(index + 1),
                        'content': pdf_reader.pages[index].extract_text()}
            docs.append(doc_page)
    for doc in docs:
        content.append(doc["content"])
        metadata.append({
            "title": doc["title"]
        })
    return content, metadata


def get_text_chunks(content, metadata):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1024,
        chunk_overlap=256,
    )
    split_docs = text_splitter.create_documents(content, metadatas=metadata)
    print(f"Split documents into {len(split_docs)} passages")
    return split_docs


def ingest_into_vectordb(split_docs):
    # embeddings = OpenAIEmbeddings()
    # embeddings = FastEmbedEmbeddings()
    embeddings = SpacyEmbeddings(model_name="en_core_web_sm")
    db = FAISS.from_documents(split_docs, embeddings)
    DB_FAISS_PATH = 'vectorstore/db_faiss'
    db.save_local(DB_FAISS_PATH)
    return db


def get_conversation_chain(vectordb):
    # llama_llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    llm = ChatGroq(model="llama3-70b-8192", temperature=0.25)
    retriever = vectordb.as_retriever()
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(llmtemplate)

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True, output_key='answer')

    conversation_chain = (ConversationalRetrievalChain.from_llm
                          (llm=llm,
                           retriever=retriever,
                           #condense_question_prompt=CONDENSE_QUESTION_PROMPT,
                           memory=memory,
                           return_source_documents=True))
    print("Conversational Chain created for the LLM using the vector store")
    return conversation_chain

def validate_answer_against_sources(response_answer, source_documents):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    similarity_threshold = 0.5  
    source_texts = [doc.page_content for doc in source_documents]

    answer_embedding = model.encode(response_answer, convert_to_tensor=True)
    source_embeddings = model.encode(source_texts, convert_to_tensor=True)

    cosine_scores = util.pytorch_cos_sim(answer_embedding, source_embeddings)


    if any(score.item() > similarity_threshold for score in cosine_scores[0]):
        return True  

    return False  

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']
    
    for i, message in enumerate(st.session_state.chat_history):
        print(i)
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            print(message.content)
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)



def main():
    load_dotenv()

    st.set_page_config(page_title="Chat with your PDFs",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")

    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)

        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                content, metadata = prepare_docs(pdf_docs)

                # get the text chunks
                split_docs = get_text_chunks(content, metadata)

                # create vector store
                vectorstore = ingest_into_vectordb(split_docs)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)


if __name__ == '__main__':
    main()