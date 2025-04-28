document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const codeGenerationForm = document.getElementById('codeGenerationForm');
    const resultsSection = document.getElementById('resultsSection');
    const loader = document.getElementById('loader');
    const resultsContent = document.getElementById('resultsContent');
    const fileTabs = document.getElementById('fileTabs');
    const codeDisplay = document.getElementById('codeDisplay');
    const downloadAllBtn = document.getElementById('downloadAllBtn');
    const downloadCurrentBtn = document.getElementById('downloadCurrentBtn');
    
    // Current state
    let currentFiles = [];
    let currentSessionId = '';
    let activeFileIndex = 0;
    
    // Initialize highlight.js
    hljs.highlightAll();
    
    // Event listeners
    codeGenerationForm.addEventListener('submit', handleFormSubmit);
    downloadAllBtn.addEventListener('click', handleDownloadAll);
    downloadCurrentBtn.addEventListener('click', handleDownloadCurrent);
    
    // Form submission handler
    async function handleFormSubmit(event) {
        event.preventDefault();
        
        // Show the results section and loader
        resultsSection.style.display = 'block';
        loader.style.display = 'flex';
        resultsContent.style.display = 'none';
        
        // Get form data
        const formData = {
            prompt: document.getElementById('prompt').value,
            enhance_prompt: document.getElementById('enhancePrompt').checked
        };
        
        try {
            // Call API to generate code
            const response = await fetch('http://localhost:8000/generate-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate code');
            }
            
            const data = await response.json();
            
            // Update current state
            currentFiles = data.files;
            currentSessionId = data.id;
            
            // Display results
            displayResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            showError(error.message);
        } finally {
            // Hide loader
            loader.style.display = 'none';
        }
    }
    
    // Display generated code results
    function displayResults(data) {
        // Show results content
        resultsContent.style.display = 'block';
        
        // Clear previous tabs
        fileTabs.innerHTML = '';
        
        // Create tabs for each file
        data.files.forEach((file, index) => {
            const tab = document.createElement('div');
            tab.className = `tab ${index === 0 ? 'active' : ''}`;
            tab.textContent = file.filename;
            tab.dataset.index = index;
            
            tab.addEventListener('click', () => {
                // Update active tab
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Update displayed code
                displayFileCode(index);
            });
            
            fileTabs.appendChild(tab);
        });
        
        // Display the first file by default
        activeFileIndex = 0;
        displayFileCode(activeFileIndex);
    }
    
    // Display code for a specific file
    function displayFileCode(index) {
        activeFileIndex = index;
        const file = currentFiles[index];
        
        // Set code content
        codeDisplay.textContent = file.content;
        
        // Set the language class for syntax highlighting
        codeDisplay.className = getLanguageClass(file.language);
        
        // Apply syntax highlighting
        hljs.highlightElement(codeDisplay);
    }
    
    // Get highlight.js language class based on file language
    function getLanguageClass(language) {
        const languageMap = {
            'html': 'html',
            'css': 'css',
            'javascript': 'javascript',
            'js': 'javascript',
            'typescript': 'typescript',
            'ts': 'typescript',
            'python': 'python',
            'py': 'python',
            'java': 'java',
            'c': 'c',
            'cpp': 'cpp',
            'c++': 'cpp',
            'csharp': 'csharp',
            'c#': 'csharp',
            'php': 'php',
            'ruby': 'ruby',
            'go': 'go',
            'rust': 'rust',
            'swift': 'swift',
            'kotlin': 'kotlin',
            'sql': 'sql',
            'json': 'json',
            'xml': 'xml',
            'yaml': 'yaml',
            'markdown': 'markdown',
            'md': 'markdown',
            'bash': 'bash',
            'shell': 'shell',
            'sh': 'shell'
        };
        
        return `hljs language-${languageMap[language.toLowerCase()] || 'plaintext'}`;
    }
    
    // Handle download all files
    function handleDownloadAll() {
        if (!currentSessionId || currentFiles.length === 0) {
            alert('No files available to download');
            return;
        }
        
        // For each file, create a download link and trigger it
        currentFiles.forEach(file => {
            downloadFile(file.filename);
        });
    }
    
    // Handle download current file
    function handleDownloadCurrent() {
        if (!currentSessionId || currentFiles.length === 0) {
            alert('No file available to download');
            return;
        }
        
        const currentFile = currentFiles[activeFileIndex];
        downloadFile(currentFile.filename);
    }
    
    // Download a specific file
    function downloadFile(filename) {
        const downloadUrl = `http://localhost:8000/download/${currentSessionId}/${filename}`;
        
        // Create a temporary anchor element to trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Show error message
    function showError(message) {
        resultsContent.style.display = 'block';
        resultsContent.innerHTML = `
            <div class="error-message">
                <h3>Error</h3>
                <p>${message}</p>
                <button onclick="location.reload()">Try Again</button>
            </div>
        `;
    }
});
