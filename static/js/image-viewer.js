const viewer = document.getElementById('imageViewer');
const imageDisplay = document.getElementById('viewerImage');
const viewerHeader = document.querySelector('.viewer-header'); 

/**
 * Closes the image viewer modal.
 */
function closeImageViewer() {
    viewer.style.display = 'none';
    imageDisplay.src = ''; 
    // Reset drag offsets if needed for central reopening
    xOffset = 0; yOffset = 0;
    viewer.style.transform = 'translateX(-50%)';
}

/**
 * Loads and displays an image from a File object using the FileReader API.
 * @param {File} fileObject - The JavaScript File object.
 */
export function showImageViewerFromFile(fileObject) {
    if (!(fileObject instanceof File)) {
        console.error("Invalid input: Not a File object.");
        return;
    }

    const reader = new FileReader();
    
    // Set up the function to run when the file is successfully read
    reader.onload = function(e) {
        // e.target.result contains the Data URL (Base64 string)
        imageDisplay.src = e.target.result;
        viewer.style.display = 'block';

        // Set the header title to the file's name
        viewerHeader.textContent = fileObject.name;
    };

    // Read the File object as a Data URL
    reader.readAsDataURL(fileObject);
}

// Ensure the close function is globally available if called from HTML
window.closeImageViewer = closeImageViewer;
window.showImageViewerFromFile = showImageViewerFromFile;

// Dragging functionality
let isDragging = false;
let currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;

function setTranslate(xPos, yPos, el) {
    el.style.transform = `translate(${xPos}px, ${yPos}px)`;
}

function dragStart(e) {
    e.preventDefault();
    if (e.target.classList.contains('viewer-header')) {
        isDragging = true;
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        viewer.style.cursor = 'grabbing';
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);
    }
}

function drag(e) {
    if (!isDragging) return;
    
    currentX = e.clientX - initialX;
    currentY = e.clientY - initialY;

    xOffset = currentX;
    yOffset = currentY;

    setTranslate(currentX, currentY, viewer);
}

function dragEnd(e) {
    isDragging = false;
    viewer.style.cursor = 'grab';
    document.removeEventListener('mousemove', drag);
    document.removeEventListener('mouseup', dragEnd);
}

if (viewerHeader) {
    viewerHeader.onmousedown = dragStart;
}
