from typing import List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import re
from pydantic import BaseModel

class CodeFile(BaseModel):
    filename: str
    language: str
    content: str

class ModelHandler:
    def __init__(self):
        # Load a lightweight model suitable for 8GB RAM
        print("Loading code generation model...")
        self.model_name = "deepseek-ai/deepseek-coder-1.3b-base"  # Small model for 8GB RAM
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Modified model loading code
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            offload_folder="./model_offload"  # Correct placement of offload_folder argument
        )
        print("Model loaded successfully!")

    def generate_code(self, prompt: str) -> List[CodeFile]:
        """Generate code files based on the provided prompt."""
        # Prepare the prompt for code generation
        full_prompt = f"""
        You are an AI that generates website code based on user requirements.
        Generate the code files needed to create the described website or application.
        For each file, specify the filename, language, and the complete code content.
        Format each file as:
        
        FILENAME: [filename with extension]
        LANGUAGE: [programming language]
        CODE:
        ```
        [actual code content]
        ```
        
        USER REQUEST: {prompt}
        
        Generate all necessary files to fulfill this request.
        """
        
        # Generate the response
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.model.device)
        output = self.model.generate(
            inputs["input_ids"],
            max_length=4096,
            temperature=0.2,
            top_p=0.95,
            num_return_sequences=1,
        )
        
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Parse the generated text to extract files
        files = self._parse_files(generated_text)
        
        # If no files were extracted, try to create some basic ones
        if not files:
            files = self._generate_fallback_files(prompt)
            
        return files

    def _parse_files(self, text: str) -> List[CodeFile]:
        """Parse the generated text to extract code files."""
        files = []
        
        # Pattern to match filename, language, and code blocks
        pattern = r"FILENAME:\s*([^\n]+)\s*LANGUAGE:\s*([^\n]+)\s*CODE:\s*```(?:[\w-]+)?\s*(.*?)```"
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            filename = match.group(1).strip()
            language = match.group(2).strip().lower()
            content = match.group(3).strip()
            
            files.append(CodeFile(
                filename=filename,
                language=language,
                content=content
            ))
        
        return files

    def _generate_fallback_files(self, prompt: str) -> List[CodeFile]:
        """Generate basic files if the model fails to produce proper output."""
        # Create basic HTML, CSS, and JS files as a fallback
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Website</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Generated Website</h1>
        <p>Based on prompt: {prompt}</p>
        <div id="content"></div>
    </div>
    <script src="script.js"></script>
</body>
</html>
"""

        css_content = """
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1 {
    color: #333;
}
"""

        js_content = """
document.addEventListener('DOMContentLoaded', function() {
    console.log('Website loaded successfully');
    
    // Add your JavaScript functionality here
    const contentDiv = document.getElementById('content');
    contentDiv.innerHTML = '<p>This is a basic generated website.</p>';
});
"""

        return [
            CodeFile(filename="index.html", language="html", content=html_content),
            CodeFile(filename="styles.css", language="css", content=css_content),
            CodeFile(filename="script.js", language="javascript", content=js_content)
        ]
