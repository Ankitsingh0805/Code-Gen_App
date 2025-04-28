import os
import uuid
import json
from typing import List, Dict, Any
from fastapi.responses import FileResponse

class FileHandler:
    def __init__(self):
        # Create output directory if it doesn't exist
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"File handler initialized with output directory: {self.output_dir}")
        
    def save_files(self, files: List[Any]) -> str:
        """Save generated code files to the local filesystem."""
        # Create a unique ID for this request
        request_id = str(uuid.uuid4())
        
        # Create a directory for this request
        request_dir = os.path.join(self.output_dir, request_id)
        os.makedirs(request_dir, exist_ok=True)
        
        # Save each file
        for file in files:
            file_path = os.path.join(request_dir, file.filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file.content)
                
        # Create a metadata file
        metadata = {
            "id": request_id,
            "files": [file.dict() for file in files]
        }
        
        metadata_path = os.path.join(request_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
            
        return request_id
        
    def get_file_path(self, request_id: str, filename: str) -> str:
        """Get the path to a specific file."""
        file_path = os.path.join(self.output_dir, request_id, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {filename} not found for request {request_id}")
            
        return file_path
        
    def serve_file(self, file_path: str):
        """Serve a file for download."""
        filename = os.path.basename(file_path)
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream"
        )
        
    def list_files(self, request_id: str) -> List[str]:
        """List all files for a specific request."""
        request_dir = os.path.join(self.output_dir, request_id)
        
        if not os.path.exists(request_dir):
            raise FileNotFoundError(f"Request directory {request_id} not found")
            
        files = os.listdir(request_dir)
        # Filter out metadata.json
        files = [f for f in files if f != "metadata.json"]
        
        return files