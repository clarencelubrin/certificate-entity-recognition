// Global variables to track state
let currentHeader = null; // The <th> currently being resized
let startX = 0;           // Initial X position of the mouse
let startWidth = 0;       // Initial width of the <th>

const table = document.getElementById('table');
const headers = table.querySelectorAll('th');

// --- MOUSE DOWN (Start Drag) ---
const mouseDownHandler = function(e) {
// Check if the click originated from the .resizer handle
if (!e.target.classList.contains('resizer')) {
    return;
}

currentHeader = e.target.parentElement;
startX = e.clientX;
startWidth = currentHeader.offsetWidth;

// Add a class to visualize the resize action
e.target.classList.add('resizing');

// Attach the move and up handlers to the whole document
document.addEventListener('mousemove', mouseMoveHandler);
document.addEventListener('mouseup', mouseUpHandler);
};

// --- MOUSE MOVE (Dragging) ---
const mouseMoveHandler = function(e) {
if (!currentHeader) {
    return;
}

const delta = e.clientX - startX;
const newWidth = startWidth + delta;

// Set the new width, preventing it from going too small
if (newWidth > 50) {
    currentHeader.style.width = `${newWidth}px`;
}
};

// --- MOUSE UP (End Drag) ---
const mouseUpHandler = function(e) {
if (!currentHeader) {
    return;
}

// Clean up: remove the resizing class and the event listeners
currentHeader.querySelector('.resizer').classList.remove('resizing');
currentHeader = null;
document.removeEventListener('mousemove', mouseMoveHandler);
document.removeEventListener('mouseup', mouseUpHandler);
};

// Attach the mousedown listener to all resizer handles
const resizers = table.querySelectorAll('.resizer');
resizers.forEach(resizer => {
    resizer.addEventListener('mousedown', mouseDownHandler);
});