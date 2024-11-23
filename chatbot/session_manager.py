import streamlit as st


class SessionManager:
    """
    Manages session state for the chatbot, including LLM selection and messages.
    """

    @staticmethod
    def initialize():
        """
        Initialize session state variables for the chatbot.
        """
        if "selected_llm" not in st.session_state:
            st.session_state.selected_llm = "OpenAI"
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "previous_llm" not in st.session_state:
            st.session_state.previous_llm = st.session_state.selected_llm

    @staticmethod
    def reset_if_llm_changed():
        """
        Reset the chat history if the user switches to a different LLM.
        """
        if st.session_state.selected_llm != st.session_state.previous_llm:
            st.session_state.messages = []
            st.session_state.previous_llm = st.session_state.selected_llm
            