from chatbot.base_chatbot import BaseChatbot
from chatbot.llm_clients import LLMClients
import streamlit as st

if __name__ == "__main__":
    # Initialize LLM clients
    llm_clients = LLMClients.initialize_clients(st.secrets)

    # Create and run the chatbot
    chatbot = BaseChatbot(llm_clients)
    chatbot.run()