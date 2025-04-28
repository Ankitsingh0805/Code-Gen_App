#!/usr/bin/env python3
import os
import subprocess
import webbrowser
import threading
import time
import sys

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def run_backend():
    """Run the FastAPI backend server."""
    backend_dir = os.path.join(PROJECT_ROOT, 'backend')
    os.chdir(backend_dir)
    subprocess.run([sys.executable, "app.py"])

def serve_frontend():
    """Serve the frontend using Python's built-in HTTP server."""
    frontend_dir = os.path.join(PROJECT_ROOT, 'frontend')
    # Check if frontend directory exists
    if not os.path.exists(frontend_dir):
        print(f"Error: Frontend directory not found at {frontend_dir}")
        print("Creating frontend directory...")
        os.makedirs(frontend_dir, exist_ok=True)
        # Create a basic index.html if it doesn't exist
        index_path = os.path.join(frontend_dir, 'index.html')
        if not os.path.exists(index_path):
            with open(index_path, 'w') as f:
                f.write("<html><body><h1>Frontend not fully set up</h1><p>Please add the frontend files to the frontend directory.</p></body></html>")
    
    os.chdir(frontend_dir)
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    
    class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            SimpleHTTPRequestHandler.end_headers(self)
    
    httpd = HTTPServer(('localhost', 8080), CORSHTTPRequestHandler)
    print(f"Frontend server started at http://localhost:8080")
    print(f"Frontend files located at: {frontend_dir}")
    httpd.serve_forever()

def open_browser():
    """Open the browser after a short delay."""
    time.sleep(3)  # Give servers time to start
    webbrowser.open('http://localhost:8080')

if __name__ == "__main__":
    # Create project directories if they don't exist
    backend_dir = os.path.join(PROJECT_ROOT, 'backend')
    frontend_dir = os.path.join(PROJECT_ROOT, 'frontend')
    output_dir = os.path.join(PROJECT_ROOT, 'output')
    model_offload_dir = os.path.join(PROJECT_ROOT, 'backend', 'model_offload')
    
    os.makedirs(backend_dir, exist_ok=True)
    os.makedirs(frontend_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(model_offload_dir, exist_ok=True)
    
    print("Starting AI Code Generator...")
    print(f"Project root: {PROJECT_ROOT}")
    
    # Start backend server in a separate thread
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Start frontend server in a separate thread
    frontend_thread = threading.Thread(target=serve_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # Open browser
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("Press Ctrl+C to quit")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        sys.exit(0)