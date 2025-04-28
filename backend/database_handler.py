from typing import List, Dict, Any, Optional
import os
import json
import time
import uuid
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

class DatabaseHandler:
    def __init__(self):
        # Initialize the embedding model
        self.sentence_transformer = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
        
        # Create collections for prompts and generated code
        self.prompt_collection = self.client.get_or_create_collection(
            name="prompts",
            embedding_function=self.sentence_transformer
        )
        
        self.sessions_collection = self.client.get_or_create_collection(
            name="sessions",
            embedding_function=self.sentence_transformer
        )
        
        print("Database initialized successfully!")
        
    def enhance_prompt(self, prompt: str) -> str:
        """Enhance the user prompt with similar previous prompts."""
        try:
            # Query for similar prompts
            results = self.prompt_collection.query(
                query_texts=[prompt],
                n_results=3
            )
            
            if not results or not results['documents'][0]:
                return prompt
                
            # Get similar prompts and their enhancements
            similar_prompts = results['documents'][0]
            
            # Create an enhanced prompt with context from previous similar prompts
            enhanced_prompt = f"""
User request: {prompt}

Consider related previous requests:
{' '.join(similar_prompts)}

Generate complete and accurate code for the user's request.
"""
            return enhanced_prompt
        except Exception as e:
            print(f"Error enhancing prompt: {str(e)}")
            return prompt
            
    def store_session(self, prompt: str, enhanced_prompt: Optional[str], files: List[Any], session_id: str):
        """Store the prompt, enhanced prompt, and generated files in the database."""
        try:
            # Store the original prompt
            self.prompt_collection.add(
                documents=[prompt],
                ids=[f"prompt_{session_id}"]
            )
            
            # Store the full session
            session_data = {
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt if enhanced_prompt else prompt,
                "files": [file.dict() for file in files],
                "timestamp": time.time(),
                "id": session_id
            }
            
            self.sessions_collection.add(
                documents=[json.dumps(session_data)],
                ids=[session_id],
                metadatas=[{"timestamp": time.time()}]
            )
            
        except Exception as e:
            print(f"Error storing session: {str(e)}")
            
    def get_history(self, limit: int = 10):
        """Get the history of code generation sessions."""
        try:
            results = self.sessions_collection.get(
                limit=limit
            )
            
            if not results or not results['documents']:
                return []
                
            sessions = []
            for doc in results['documents']:
                try:
                    session_data = json.loads(doc)
                    sessions.append(session_data)
                except:
                    continue
                
            # Sort by timestamp, newest first
            sessions.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            return sessions
            
        except Exception as e:
            print(f"Error getting history: {str(e)}")
            return []