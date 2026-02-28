document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('audio-input');
    const fileInfo = document.getElementById('file-info');
    const fileNameDisplay = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file');
    const generateBtn = document.getElementById('generate-btn');
    
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');
    const resultsSection = document.getElementById('results-section');
    const errorMessage = document.getElementById('error-message');
    const retryBtn = document.getElementById('retry-btn');
    
    let currentFile = null;

    // --- Drag & Drop Handlers ---
    dropZone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length) handleFile(files[0]);
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length) handleFile(this.files[0]);
    });

    function handleFile(file) {
        // Validate Extensions explicitly to match python backend
        if (!file.type.startsWith('audio/') && !file.name.match(/\.(mp3|wav|m4a|ogg|flac)$/i)) {
            alert('Please upload an audio file (MP3, WAV, M4A, OGG).');
            return;
        }
        
        // Max 50MB
        if (file.size > 50 * 1024 * 1024) {
            alert('File is too large. Max size is 50MB.');
            return;
        }

        currentFile = file;
        fileNameDisplay.textContent = file.name;
        dropZone.classList.add('hidden');
        fileInfo.classList.remove('hidden');
        generateBtn.disabled = false;
    }

    removeFileBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        dropZone.classList.remove('hidden');
        fileInfo.classList.add('hidden');
        generateBtn.disabled = true;
    });

    // --- Generate Processing ---
    generateBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI Updates
        generateBtn.classList.add('hidden');
        fileInfo.classList.add('hidden');
        errorState.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loadingState.classList.remove('hidden');

        // Prepare FormData
        const formData = new FormData();
        formData.append('audio', currentFile);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Server error occurred');
            }

            // Populate Data - Using marked for markdown to HTML conversion
            document.getElementById('notes').innerHTML = marked.parse(data.notes || 'No notes generated.');
            document.getElementById('flashcards').innerHTML = marked.parse(data.flashcards || 'No flashcards generated.');
            document.getElementById('quiz').innerHTML = marked.parse(data.quiz || 'No quiz generated.');
            document.getElementById('transcript').innerHTML = marked.parse(data.transcript || 'No transcript available.');

            loadingState.classList.add('hidden');
            resultsSection.classList.remove('hidden');
            
            // Allow them to upload a new one simultaneously
            dropZone.classList.remove('hidden');
            currentFile = null;
            fileInput.value = '';

        } catch (error) {
            loadingState.classList.add('hidden');
            errorState.classList.remove('hidden');
            errorMessage.textContent = error.message;
            dropZone.classList.remove('hidden');
            currentFile = null;
            fileInput.value = '';
        }
    });

    retryBtn.addEventListener('click', () => {
        errorState.classList.add('hidden');
        dropZone.classList.remove('hidden');
        generateBtn.classList.remove('hidden');
        generateBtn.disabled = true;
    });

    // --- Tab Switching ---
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });
});
