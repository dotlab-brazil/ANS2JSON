// Configurações
const CONFIG = {
    API_ENDPOINT: 'http://127.0.0.1:5051/api/v1/digitalizar',
    MAX_UPLOAD_MB: 50,
    MAX_FOLDER_FILES: 10,
    TIMEOUT_MS: 30000
};

// Elementos da UI
const UI_ELEMENTS = {
    uploadForm: document.getElementById('upload-form'),
    feedbackArea: document.getElementById('feedback-area'),
    processingFeedback: document.getElementById('processing-feedback'),
    errorMessage: document.getElementById('error-message'),
    resultsArea: document.getElementById('results-area'),
    resultadoJson: document.getElementById('resultado-json'),
    singleFileInput: document.getElementById('single-file-input'),
    folderInput: document.getElementById('folder-input'),
    cameraBox: document.getElementById('camera-box'),
    limitText: document.getElementById('limit-text'),
    cameraModalElement: document.getElementById('camera-modal'),
    captureBtn: document.getElementById('capture-btn'),
    video: document.getElementById('camera-stream'),
    canvas: document.getElementById('camera-canvas'),
    downloadBtn: document.getElementById('download-json')
};

// Funções de UI
const UI = {
    reset: () => {
        UI_ELEMENTS.feedbackArea.style.display = 'none';
    },
    
    showProcessing: () => {
        UI.reset();
        UI_ELEMENTS.feedbackArea.style.display = 'block';
        UI_ELEMENTS.processingFeedback.style.display = 'block';
        UI_ELEMENTS.errorMessage.style.display = 'none';
        UI_ELEMENTS.resultsArea.style.display = 'none';
    },
    
    showError: (message) => {
        UI.reset();
        UI_ELEMENTS.feedbackArea.style.display = 'block';
        UI_ELEMENTS.errorMessage.textContent = message;
        UI_ELEMENTS.errorMessage.style.display = 'block';
        UI_ELEMENTS.processingFeedback.style.display = 'none';
        UI_ELEMENTS.resultsArea.style.display = 'none';
    },
    
    showResults: (data) => {
        UI.reset();
        UI_ELEMENTS.feedbackArea.style.display = 'block';
        UI_ELEMENTS.resultadoJson.textContent = JSON.stringify(data, null, 2);
        UI_ELEMENTS.resultsArea.style.display = 'block';
        UI_ELEMENTS.processingFeedback.style.display = 'none';
        UI_ELEMENTS.errorMessage.style.display = 'none';
    },
    
    setupDownload: (data) => {
        UI_ELEMENTS.downloadBtn.onclick = () => {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'resultado-anatomico.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        };
    }
};

// Funções utilitárias
const Utils = {
    validateFiles: (files, isFolder = false) => {
        if (!files || files.length === 0) {
            throw new Error('Nenhum arquivo para enviar.');
        }
        
        if (isFolder && files.length > CONFIG.MAX_FOLDER_FILES) {
            throw new Error(`O envio de pastas está limitado a ${CONFIG.MAX_FOLDER_FILES} arquivos.`);
        }

        const totalSize = Array.from(files).reduce((acc, file) => acc + file.size, 0);
        if (totalSize > CONFIG.MAX_UPLOAD_MB * 1024 * 1024) {
            throw new Error(`Tamanho total excede o limite de ${CONFIG.MAX_UPLOAD_MB} MB.`);
        }
        
        return true;
    }
};

// Lógica principal
const App = {
    init: () => {
        console.log("Aplicação inicializada");
        UI_ELEMENTS.limitText.textContent = `(Limite total: ${CONFIG.MAX_UPLOAD_MB} MB)`;
        
        // Event listeners
        UI_ELEMENTS.uploadForm.addEventListener('submit', (e) => e.preventDefault());
        
        UI_ELEMENTS.singleFileInput?.addEventListener('change', (e) => 
            App.handleUpload(e.target.files));
        
        UI_ELEMENTS.folderInput?.addEventListener('change', (e) => 
            App.handleUpload(e.target.files, true));
        
        App.setupCamera();
    },
    
    handleUpload: async (files, fromFolder = false) => {
        try {
            Utils.validateFiles(files, fromFolder);
            
            UI.showProcessing();
            
            const formData = new FormData();
            Array.from(files).forEach(file => formData.append('image_files', file));
            
            const response = await fetch(`${CONFIG.API_ENDPOINT}?format=json`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erro no servidor');
            }
            
            const data = await response.json();
            UI.showResults(data);
            UI.setupDownload(data);
        } catch (error) {
            UI.showError(`Erro: ${error.message}`);
        }
    },
    
    setupCamera: () => {
        if (!UI_ELEMENTS.cameraBox) return;
        
        const cameraModal = new bootstrap.Modal(UI_ELEMENTS.cameraModalElement);
        let stream = null;
        
        UI_ELEMENTS.cameraBox.addEventListener('click', async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: "environment" } 
                });
                UI_ELEMENTS.video.srcObject = stream;
            } catch (err) {
                UI.showError('Não foi possível acessar a câmera.');
                cameraModal.hide();
            }
        });
        
        const stopCamera = () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            stream = null;
        };
        
        UI_ELEMENTS.captureBtn.addEventListener('click', () => {
            UI_ELEMENTS.canvas.width = UI_ELEMENTS.video.videoWidth;
            UI_ELEMENTS.canvas.height = UI_ELEMENTS.video.videoHeight;
            UI_ELEMENTS.canvas.getContext('2d').drawImage(UI_ELEMENTS.video, 0, 0);
            
            UI_ELEMENTS.canvas.toBlob(blob => {
                const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
                App.handleUpload([file]);
            }, 'image/jpeg');
            
            stopCamera();
            cameraModal.hide();
        });
        
        UI_ELEMENTS.cameraModalElement.addEventListener('hidden.bs.modal', stopCamera);
    }
};

// Inicialização
document.addEventListener('DOMContentLoaded', App.init);