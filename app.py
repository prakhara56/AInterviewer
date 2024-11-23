import streamlit as st
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


# Initialization and Configurations
def initialize_llm_clients():
    azure_client = AzureChatOpenAI(
        azure_deployment=st.secrets["AZURE_OPENAI_DEPLOYMENT_NAME"],
        azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
        api_version=st.secrets["AZURE_OPENAI_VERSION"],
        api_key=st.secrets["AZURE_OPENAI_API_KEY"],
    )

    gemini_client = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        api_key=st.secrets["GOOGLE_API_KEY"],
    )

    return {"OpenAI": azure_client, "Gemini": gemini_client}


def initialize_session_state():
    if "selected_llm" not in st.session_state:
        st.session_state.selected_llm = "OpenAI"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "previous_llm" not in st.session_state:
        st.session_state.previous_llm = st.session_state.selected_llm


def reset_chat_if_llm_changed():
    if st.session_state.selected_llm != st.session_state.previous_llm:
        st.session_state.messages = []
        st.session_state.previous_llm = st.session_state.selected_llm
        st.rerun()
        st.success("LLM changed! Chat reset.")


# Chat Processing
def process_user_input(prompt, current_client):
    # Reset chat if LLM changed
    reset_chat_if_llm_changed()

    # Append user input to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant's response
    with st.chat_message("assistant"):
        try:
            response_stream = current_client.stream(
                [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            response_content = st.write_stream(response_stream)  # Combine stream chunks for storage
            st.session_state.messages.append({"role": "assistant", "content": response_content})
        except Exception as e:
            response_content = f"Error: {e}"
            st.error(response_content)
    st.session_state.messages.append({"role": "assistant", "content": response_content})

# Sidebar and Chat Interface
def render_sidebar():
    with st.sidebar:
        st.title("🤖💬 Chatbot")

        # Dropdown to choose LLM
        st.session_state.selected_llm = st.selectbox(
            "Choose LLM:", options=["OpenAI", "Gemini"], index=0
        )
        reset_chat_if_llm_changed()

        # Display the selected LLM
        st.write(f"### Selected LLM: {st.session_state.selected_llm}")

        # Button to clear chat history
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.success("Chat history cleared!")


def render_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main():
    st.title("Chat Bot")

    # Initialize clients and session state
    llm_clients = initialize_llm_clients()
    initialize_session_state()

    # Update current client based on selection
    current_client = llm_clients[st.session_state.selected_llm]

    # Render sidebar and chat history
    render_sidebar()
    render_chat_history()

    # Chat input section
    if prompt := st.chat_input("Type 'hi' to start or ask anything!"):
        process_user_input(prompt, current_client)


if __name__ == "__main__":
    main()