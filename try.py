from Functionalities_Setup.PDF_reader import PDFLoader
from Functionalities_Setup.Chunking import Chunker
from langchain_openai import AzureOpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import json
# from dotenv import load_dotenv
# load_dotenv()


load_pdf = PDFLoader(file_path="/Users/prakharagarwal/Documents/PDF samples/sample_research.pdf")
docs = load_pdf.load()
# print(docs)


# embedder = AzureOpenAIEmbeddings(
#     azure_deployment=os.environ["embedding_openai_model_name"],
#     openai_api_version=os.environ["embedding_openai_api_version"]
# )

embedder = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
chunker = Chunker()
chunks = chunker.semantic_chunking(docs,embedder)
# print(chunks)
json_data = [
    {
        "metadata": doc.metadata,
        "page_content": doc.page_content
    }
    for doc in chunks
]

# Define the output file path
output_file_path = "chunks_data.json"

# Save the data to a JSON file
with open(output_file_path, "w") as json_file:
    json.dump(json_data, json_file, indent=4)

print(f"Data saved to {output_file_path}")


