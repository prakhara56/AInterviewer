from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.embeddings import Embeddings
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import Optional, Union, List, Dict, Any



class Chunker:
    def __init__(self):
        pass
    def recursive_chunking(
        self, 
        text: List[Optional[Union[str, Document]]],
        chunk_size: int = 1000, 
        chunk_overlap: int = 0
    ) -> List[Document]:
        """
        Perform recursive chunking on a list of text strings or Document objects.
        
        Args:
            text (List[Optional[Union[str, Document]]]): A list of text strings or Document objects to be chunked.
            chunk_size (int): The maximum size of each chunk. Default is 1000.
            chunk_overlap (int): The number of overlapping characters between chunks. Default is 0.
            
        Returns:
            List[Document]: A list of chunked Document objects.
        """
        # Initialize the text splitter with desired chunk size and overlap
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Result container for the chunks
        chunked_documents = []
        
        if all(isinstance(item, str) for item in text):  # If all input items are raw text strings
            chunked_documents = text_splitter.create_documents(text)
        elif all(isinstance(item, Document) for item in text):  # If all input items are Document objects
            chunked_documents = text_splitter.split_documents(text)
        else:
            raise ValueError(
                "Unsupported type. Input must be a list of strings or a list of Document objects."
            )
    
        return chunked_documents
    
    def semantic_chunking(
        self, 
        text: List[Optional[Union[str, Document]]] = [],
        embeddings: Optional[Embeddings] = None,
    ) -> List[Document]:
        """
        Perform semantic chunking on a list of text or Document objects.
        
        Args:
            text (List[Optional[Union[str, Document]]]): A list of text strings or Document objects.
            
        Returns:
            List[Document]: A list of chunked Document objects.
        """

        # Initialize the text splitter with desired chunk size and overlap
        text_splitter = SemanticChunker(embeddings=embeddings)
        
        # Result container for the chunks
        chunked_documents = []
        
        if all(isinstance(item, str) for item in text):  # If all input items are raw text strings
            chunked_documents = text_splitter.create_documents(text)
        elif all(isinstance(item, Document) for item in text):  # If all input items are Document objects
            chunked_documents = text_splitter.split_documents(text)
        else:
            raise ValueError(
                "Unsupported type. Input must be a list of strings or a list of Document objects."
            )
    
        return chunked_documents