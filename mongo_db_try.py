from pymongo import MongoClient
from urllib.parse import quote_plus
import os

# Replace these with your actual MongoDB credentials
username = os.getenv("MONGO_DB_USERNAME")  
password = os.getenv("MONGO_DB_PASSWORD")  

# Encode the username and password
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# Correct connection string with encoded credentials
connection_string = f"mongodb+srv://{encoded_username}:{encoded_password}@rag-cluster.m2w3p.mongodb.net/?retryWrites=true&w=majority&appName=RAG-Cluster"

# Connect to MongoDB
try:
    client = MongoClient(connection_string)
    db = client.test  # Replace 'test' with your database name if needed
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error: {e}")