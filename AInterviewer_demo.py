#!/usr/bin/env python
# coding: utf-8

# To run this file use this command on terminal: C:\Users\d.abhinav\AppData\Roaming\Python\Python311\Scripts\streamlit.exe run AInterviewer_demo.py

from dataclasses import dataclass
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA, ConversationChain
from langchain.prompts.prompt import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import NLTKTextSplitter
from PyPDF2 import PdfReader
from typing import Literal

import nltk
import os
import streamlit as st

os.environ['OPENAI_API_KEY'] = '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'

@dataclass
class Message:
    """Class for keeping track of interview history."""
    origin: Literal["human", "ai"]
    message: str

def save_vector(jd):
    """embeddings"""
    nltk.download('punkt')
    pdf_reader = PdfReader(jd)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    # Split the document into chunks
    text_splitter = NLTKTextSplitter()
    texts = text_splitter.split_text(text)

    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts, embeddings)
    return docsearch

def initialize_session_state(jd):
    
    # convert jd to embeddings
    if 'docsearch' not in st.session_state:
        st.session_state.docserch = save_vector(jd)
    
    # retriever
    if 'retriever' not in st.session_state:
        st.session_state.retriever = st.session_state.docserch.as_retriever(search_type="similarity")
    
    if 'jd_chain_type_kwargs' not in st.session_state:
        
        jd_template = """I want you to act as an interviewer. Remember, you are the interviewer not the candidate. 
            
            Let think step by step.
            
            Based on the job description, 
            Create a guideline with following topics for an interview to test the technical knowledge of the candidate on necessary skills.
            
            For example:
            If the job description requires knowledge of data mining, AInterviewer will ask you questions like "Explains overfitting or How does backpropagation work?"
            If the job description requrres knowldge of statistics, AInterviewer will ask you questions like "What is the difference between Type I and Type II error?"
            
            Don't include these example questions in the guidline. They are just for your reference.
            Do not ask the same question.
            Do not repeat the question. 
            
            Job Description: 
            {context}
            
            Question: {question}
            Answer: """

        Interview_Prompt = PromptTemplate(input_variables=["context", "question"],
                                          template=jd_template)
        st.session_state.jd_chain_type_kwargs = {"prompt": Interview_Prompt}
    
    # interview history
    if "jd_history" not in st.session_state:
        st.session_state.jd_history = []
        st.session_state.jd_history.append(Message(origin="ai", message="Hello, I am your interivewer today. I will ask you some questions based on the job description. Please start by saying hello or introducing yourself."))
    
    # memory buffer
    if "jd_memory" not in st.session_state:
        st.session_state.jd_memory = ConversationBufferMemory(human_prefix = "Candidate: ", ai_prefix = "Interviewer")
    
    # guideline
    if "jd_guideline" not in st.session_state:
        llm = ChatOpenAI(
        model_name = "gpt-3.5-turbo",
        temperature = 0.5,)

        st.session_state.jd_guideline = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type_kwargs=st.session_state.jd_chain_type_kwargs, chain_type='stuff',
            retriever=st.session_state.retriever, memory = st.session_state.jd_memory).run("Create an interview guideline and prepare only two questions for each topic. Make sure the questions test the technical knowledge")
    
    # llm chain
    if "jd_screen" not in st.session_state:
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7, )

        PROMPT = PromptTemplate(
            input_variables=["history", "input"],
            template= """I want you to act as an interviewer strictly following the guideline in the current conversation.
            
            Ask me questions and wait for my answers like a human. Do not write explanations.
            Candidate has no assess to the guideline.
            Only ask one question at a time. 
            Do ask follow-up questions if you think it's necessary.
            If no follow-up is required proceed to the next question once candidate has answered.
            Do not repeat the question.
            Candidate has no assess to the guideline.
            Your name is AInterviewer.
            I want you to only reply as an interviewer.
            Don't give answers to the candidate if he is not able to answer and move on to the next question.
            Do not write all the conversation at once.
            Candidate has no assess to the guideline.
            
            Current Conversation:
            {history}
            
            Candidate: {input}
            AI: """)
        
        st.session_state.jd_screen =  ConversationChain(prompt=PROMPT, llm = llm, memory = st.session_state.jd_memory)
    
    # llm chain for generating feedback
    if "feedback" not in st.session_state:
        
        feedback_template = """ Based on the chat history, I would like you to evaluate the candidate based on the following format:
                Summarization: summarize the conversation from the provided history in a short paragraph.
              
                Strength: Give positive feedback to the candidate based on the conversation history. 
               
                Weakness: Tell the candidate what topics he/she can improve on based on the conversation history.
                
                Sample Answers: Provide sample answers to each of the questions asked by the ai interviewer in the conversation history.
               
              The evaluation should be done solely on the basis of the technical knowledge of the candidate.
              Don't judge the candidate on his english grammer or sentence formation skills.
              
              Remember, the candidate has no idea what the interview guideline is.
              Don't provide sample answers for all the questions in the guidline.
              Only provide sample answers for the questions asked by the AI assisstant as present in the conversation history.
              
              Sometimes the candidate may not even answer the question.

              Conversation history:
              {history}

              Interviewer: {input}
              Response: """
        
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.5,)
        st.session_state.feedback = ConversationChain(
            prompt=PromptTemplate(input_variables=["history", "input"], template=feedback_template),
            llm=llm,
            memory=st.session_state.jd_memory,
        )


def main():
    st.set_page_config(page_title="AInterviewer")
    st.markdown("<h1> Hello my name is AInterviewer 👋 </h1>", unsafe_allow_html=True)
    st.write("Upload the Job description to start")

    with st.sidebar:
        jd =  st.file_uploader("Upload PDF file of Job Description",type=["pdf"])
    
    if jd:
        initialize_session_state(jd)  
        
        feedback = st.button("Get Interview Feedback")

        chat_placeholder = st.container()
        answer_placeholder = st.container()

        with st.sidebar:
            guideline = st.button("Show me interview guideline!")
            if guideline:
                with st.expander("Guidline"):
                    st.markdown(st.session_state.jd_guideline)
   
        if feedback:
            evaluation = st.session_state.feedback.run("please give evalution regarding the interview")
            st.markdown(evaluation)
            st.download_button(label="Download Interview Feedback", data=evaluation, file_name="interview_feedback.txt")
            st.stop()

        else:
            
            with answer_placeholder:
                answer = st.chat_input("Your answer")
                if answer:
                    st.session_state['answer'] = answer
                    st.session_state.jd_history.append(Message("human", answer))
                    llm_answer = st.session_state.jd_screen.run(answer)
                    st.session_state.jd_history.append(Message("ai", llm_answer))
            
            with chat_placeholder:
                for answer in st.session_state.jd_history:
                    if answer.origin == 'ai':
                        with st.chat_message("assistant"):
                            st.write(answer.message)
                    else:
                        with st.chat_message("user"):
                            st.write(answer.message)

                    

if __name__ == "__main__":
    main()