import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from fastapi import FastAPI, UploadFile, HTTPException
import PyPDF2
import tempfile

app = FastAPI()

# Initialize LangChain Components
openai_api_key = "your_openai_api_key"
embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Initialize FAISS
faiss_index = None

# Global Session States
session_state = {
    "job_description_embedding": None,
    "conversation_history": [],
    "guidelines": None
}

### Functions for Modular Workflow ###

def extract_text_from_pdf(file: UploadFile) -> str:
    """Extract text from an uploaded PDF."""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.file.read())
            temp_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(temp_file.name)
            text = ''.join(page.extract_text() for page in pdf_reader.pages)
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read PDF: {e}")

def generate_embedding(text: str) -> None:
    """Generate and store embeddings using OpenAI and FAISS."""
    global faiss_index
    embedding = embedding_model.embed_query(text)
    faiss_index = FAISS.from_vectors([embedding], embedding_model)

def generate_interview_guidelines(text: str) -> str:
    """Generate interview guidelines based on job description."""
    prompt = PromptTemplate(input_variables=["description"], template="""
    Based on the job description below, generate detailed interview guidelines.
    Job Description:
    {description}
    """)
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
    return llm(prompt.format(description=text))

def initialize_session_states(job_description: str):
    """Initialize embeddings and guidelines in session states."""
    session_state["job_description_embedding"] = generate_embedding(job_description)
    session_state["guidelines"] = generate_interview_guidelines(job_description)

def get_guidelines() -> str:
    """Return the stored guidelines."""
    if not session_state["guidelines"]:
        raise HTTPException(status_code=400, detail="Guidelines not generated yet.")
    return session_state["guidelines"]

def ask_question(user_input: str) -> str:
    """Generate the next question or response based on user input."""
    memory = ConversationBufferMemory()
    conversation = ConversationChain(
        llm=OpenAI(openai_api_key=openai_api_key),
        memory=memory
    )
    response = conversation.run(input=user_input)
    session_state["conversation_history"].append({"user_input": user_input, "response": response})
    return response

def generate_feedback() -> str:
    """Generate feedback on the user's input."""
    history = session_state["conversation_history"]
    feedback_prompt = PromptTemplate(input_variables=["history"], template="""
    Evaluate the user's responses and provide detailed feedback based on the conversation history.
    Conversation History:
    {history}
    """)
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
    return llm(feedback_prompt.format(history=history))

### FastAPI Endpoints ###

@app.post("/upload_job_description/")
async def upload_job_description(file: UploadFile):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF.")
    job_description = extract_text_from_pdf(file)
    initialize_session_states(job_description)
    return {"message": "Job description processed and session initialized."}

@app.get("/get_guidelines/")
async def get_guidelines_endpoint():
    return {"guidelines": get_guidelines()}

@app.post("/ask_question/")
async def ask_question_endpoint(user_input: str):
    response = ask_question(user_input)
    return {"response": response}

@app.get("/generate_feedback/")
async def generate_feedback_endpoint():
    feedback = generate_feedback()
    return {"feedback": feedback}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)