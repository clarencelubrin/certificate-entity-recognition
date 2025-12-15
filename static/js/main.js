import { uploadImageForOCR, sendToGeminiAPI, checkGeminiAPIAvailability } from './api.js';
import { showImageViewerFromFile } from './image-viewer.js';
// File Queue
let fileQueue = [];
let fileHistory = [];
let isRendering = false;

window.addEventListener("DOMContentLoaded", () => {
    // Buttons
    const uploadButton = document.getElementById('upload-button');
    const runButton = document.getElementById('run-button');
    const clearButton = document.getElementById('clear-button');
    const downloadButton = document.getElementById('download-button');
    const clearTableButton = document.getElementById('clear-table-button');
    const dropArea = document.querySelector('.drag-drop-area-container');
    const dropAreaContent = document.querySelector('.drag-drop-area-content');
    const modelSelect = document.getElementById('model-select');

    const queueContainer = document.getElementById('queue-container');
    const resultsTableBody = document.getElementById('results-body');

    // Modal
    const modal = document.getElementById('modal');

    // Handle button clicks
    uploadButton.addEventListener('click', () => {
        modal.hidden = false;
    });
    downloadButton.addEventListener('click', () => {
        const resultsTableBody = document.getElementById('results-body');
        let csvContent = "data:text/csv;charset=utf-8,";

        // Add headers
        const headers = ["TYPE", "AWARDEE", "ROLE", "EVENT", "DATE", "LOCATION", "SIGNATORIES", "FILE LOCATION"];
        csvContent += headers.join(",") + "\n";

        // Add rows, carefully handling commas and quotes in the data
        Array.from(resultsTableBody.rows).forEach(row => {
            const rowData = Array.from(row.cells).map(cell => {
                const cellText = cell.textContent.replace(/"/g, '""');
                return `"${cellText}"`;
            });
            csvContent += rowData.join(",") + "\n";
        });

        const encodedUri = encodeURI(csvContent);

        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        
        link.setAttribute("download", "ocr_results.csv"); 

        document.body.appendChild(link); // Append is necessary for some browsers (like Firefox)
        link.click();
        document.body.removeChild(link);
        
    });
    // Clear file queue
    clearButton.addEventListener('click', () => {
        fileQueue = [];
        updateQueueDisplay(queueContainer);
    });
    function disableControls() {
        // Set cursor to loading
        document.body.style.cursor = 'wait';
        runButton.disabled = true;
        clearButton.disabled = true;
        uploadButton.disabled = true;
        isRendering = true;
    }
    function enableControls() {
        document.body.style.cursor = 'default';
        runButton.disabled = false;
        clearButton.disabled = false;
        uploadButton.disabled = false;
        isRendering = false;
    }
    runButton.addEventListener('click', async () => {
        disableControls();
        if (modelSelect.value === 'gemini') {
            let response;
            console.log('Selected model: Gemini API');
            while(true) {
                response = await checkGeminiAPIAvailability();
                if(response) break;
            }
            // Check if Gemini API is available
            if(!response.has_gemini_api) {
                alert('Gemini API is not available on the server. Please provide a valid API key (Gemini 2.5 Flash) or select another model.');
                enableControls();
                return;
            }
        }
        let repeat = 0;
        while(fileQueue.length > 0) {
            // Set the first element in the queue to processing state
            const queueContainer = document.getElementById('queue-container');
            const firstFileDiv = queueContainer.querySelector('.file-item');
            let response;
            if (firstFileDiv) {
                firstFileDiv.classList.add('processing');
            }
            if (modelSelect.value === 'gemini') {
                response = await sendToGeminiAPI(fileQueue[0]);
                console.log('Gemini API response:', response);
            } else {
                response = await uploadImageForOCR(fileQueue[0]);
                response = response.extracted_text;
            }

            if(!response) {
                console.error('No response received for file:', fileQueue[0]);
                await new Promise(resolve => setTimeout(resolve, 2000));
                repeat += 1;
                if(repeat >= 3) {
                    console.error('Maximum retry attempts reached for file:', fileQueue[0]);
                    enableControls();
                    return;
                }
                continue;
            }
            fileHistory.push(fileQueue[0]);
            // Pop the processed file from the queue
            fileQueue.shift();
            updateQueueDisplay(queueContainer);
            addResultToTable(response, resultsTableBody);
        }
        // Reset cursor to default
        enableControls()
    });
    clearTableButton.addEventListener('click', () => {
        const resultsTableBody = document.getElementById('results-body');
        resultsTableBody.innerHTML = '';
    });
    // Close modal when clicking outside of it
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.hidden = true;
        }
    });
    // When user dragged file to the window, show the modal
    window.addEventListener('dragover', (event) => {
        event.preventDefault();
        modal.hidden = false;
    });

    // Handle drag and drop on modal file and adding to fileQueue
    modal.addEventListener('dragover', (event) => {
        event.preventDefault();
        modal.classList.add('dragover');
        dropArea.classList.add('is-dragged');
        dropAreaContent.innerHTML = '<p>Release to <b>upload files</b></p>';
    });
    modal.addEventListener('dragleave', (event) => {
        event.preventDefault();
        modal.classList.remove('dragover');
        dropArea.classList.remove('is-dragged');
        dropAreaContent.innerHTML = '<p>Click to <b>browse</b> or <b>drag images here</b></p>';
    });
    modal.addEventListener('drop', (event) => {
        event.preventDefault();
        modal.classList.remove('dragover');
        dropArea.classList.remove('is-dragged');
        dropAreaContent.innerHTML = '<p>Click to <b>browse</b> or <b>drag images here</b></p>';
        const files = event.dataTransfer.files;
        for (let i = 0; i < files.length; i++) {
            fileQueue.push(files[i]);
        }
        updateQueueDisplay(queueContainer);
        modal.hidden = true;
    });
    dropArea.addEventListener('click', () => {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.multiple = true;
        fileInput.accept = 'image/*';
        fileInput.addEventListener('change', (event) => {
            const files = event.target.files;
            for (let i = 0; i < files.length; i++) {
                fileQueue.push(files[i]);
            }
            updateQueueDisplay(queueContainer);
            modal.hidden = true;
        });
        fileInput.click();
    });
});

/**
 * Updates the visual display of the file queue.
 * @param {HTMLElement} queueContainer 
 */
function updateQueueDisplay(queueContainer) {
    queueContainer.innerHTML = '';
    fileQueue.forEach((file, index) => {
        const fileDiv = document.createElement('div');
        const imageThumbnail = document.createElement('img');
        const removeButton = document.createElement('button');

        fileDiv.className = 'file-item';
        fileDiv.textContent = file.name;

        imageThumbnail.src = URL.createObjectURL(file);
        imageThumbnail.className = 'file-thumbnail';

        removeButton.className = 'remove-file-button';
        removeButton.textContent = '×';
        removeButton.addEventListener('click', () => {
            if(isRendering) return; // Prevent removal during rendering
            fileQueue.splice(index, 1);
            updateQueueDisplay(queueContainer);
        });

        fileDiv.prepend(imageThumbnail);
        fileDiv.appendChild(removeButton);
        queueContainer.appendChild(fileDiv);
    });
    console.log('Current file queue:', fileQueue);
}

/**
 * Adds a result row to the results table.
 * @param {Object[]} result 
 * @param {HTMLElement} resultsTableBody 
 * @returns none
 */
function addResultToTable(result, resultsTableBody) {
    if (!result) return;

    const CATEGORIES = ["TYPE", "AWARDEE", "ROLE", "EVENT", "DATE", "LOCATION", "SIGNATORIES"]
    const row = document.createElement('tr');

    for (const category of CATEGORIES) {
        const valueCell = document.createElement('td');
        valueCell.className = 'table-cell';
        const inputCell = document.createElement('div');
        inputCell.contentEditable = true;
        inputCell.textContent = result[category] || '';
        inputCell.className = 'input-cell';
        valueCell.appendChild(inputCell);
        row.appendChild(valueCell);
    }
    const filelocationCell = document.createElement('td');
    filelocationCell.className = 'file-location-cell';
    // Set the text content to the file name
    filelocationCell.textContent = fileHistory[fileHistory.length - 1].name;
    const file = fileHistory[fileHistory.length - 1];
    filelocationCell.addEventListener('click', () => {
        // Show the floating window image viewer
        if (file instanceof File) {
            // Call the function with the File object
            showImageViewerFromFile(file); 
        } else {
            alert('No image file object available for this record.');
        }
    });

    row.appendChild(filelocationCell);
    resultsTableBody.appendChild(row);
} 
