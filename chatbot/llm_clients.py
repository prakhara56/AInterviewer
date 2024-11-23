from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


class LLMClients:
    """
    Initializes and manages different LLM clients for use in the chatbot.
    """

    @staticmethod
    def initialize_clients(secrets):
        """
        Initialize Azure OpenAI and Google Gemini clients.

        Args:
            secrets (dict): Secret keys and configurations for LLMs.

        Returns:
            dict: A dictionary of initialized LLM clients.
        """
        azure_client = AzureChatOpenAI(
            azure_deployment=secrets["AZURE_OPENAI_DEPLOYMENT_NAME"],
            azure_endpoint=secrets["AZURE_OPENAI_ENDPOINT"],
            api_version=secrets["AZURE_OPENAI_VERSION"],
            api_key=secrets["AZURE_OPENAI_API_KEY"],
        )

        gemini_client = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=secrets["GOOGLE_API_KEY"],
        )

        return {"OpenAI": azure_client, "Gemini": gemini_client}