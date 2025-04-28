from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
import json
from model_handler import ModelHandler
from database_handler import DatabaseHandler
from file_handler import FileHandler

app = FastAPI(title="AI Code Generator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers
model_handler = ModelHandler()
db_handler = DatabaseHandler()
file_handler = FileHandler()

class CodeRequest(BaseModel):
    prompt: str
    enhance_prompt: bool = True

class CodeFile(BaseModel):
    filename: str
    language: str
    content: str

class CodeResponse(BaseModel):
    prompt: str
    enhanced_prompt: Optional[str] = None
    files: List[CodeFile]
    id: str

@app.post("/generate-code", response_model=CodeResponse)
async def generate_code(request: CodeRequest):
    try:
        # Process the prompt
        prompt = request.prompt
        
        # Enhance prompt with vector search if requested
        enhanced_prompt = None
        if request.enhance_prompt:
            enhanced_prompt = db_handler.enhance_prompt(prompt)
            generation_prompt = enhanced_prompt
        else:
            generation_prompt = prompt
        
        # Generate code using the model
        files = model_handler.generate_code(generation_prompt)
        
        # Save the generated code to local storage
        request_id = file_handler.save_files(files)
        
        # Store the prompt and result in the vector database
        db_handler.store_session(prompt, enhanced_prompt, files, request_id)
        
        return CodeResponse(
            prompt=prompt,
            enhanced_prompt=enhanced_prompt,
            files=files,
            id=request_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{request_id}/{filename}")
async def download_file(request_id: str, filename: str):
    try:
        file_path = file_handler.get_file_path(request_id, filename)
        return file_handler.serve_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")

@app.get("/history", response_model=List[CodeResponse])
async def get_history():
    try:
        history = db_handler.get_history()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)