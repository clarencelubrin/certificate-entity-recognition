/**
 * Uploads an image file to the Python FastAPI server for OCR processing.
 * @param {File} fileBlobOrInput 
 * @returns {Promise<Object>} The OCR result as a JSON object.
 */
export async function uploadImageForOCR(fileBlobOrInput) {
  const url = `/process_ocr`;
  const formData = new FormData();
  
  formData.append('image_file', fileBlobOrInput, 'certificate.png'); // The third argument is the filename

  try {
    console.log("Sending image to Python Sidecar...");
    
    const response = await fetch(url, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
        const errorDetail = await response.json();
        throw new Error(`[ ERROR ] API error: ${response.status} - ${errorDetail.detail}`);
    }

    const data = await response.json();
    console.log("[ SUCCESS ] OCR Result Received:", data);
    return data;
    
  } catch (error) {
    console.error('[ ERROR ] Error during image upload:', error);
  }
}

/**
 * Google Gemini API
 * Sends a prompt to the Gemini API and retrieves the response.
 * @param {File} fileBlobOrInput
 * @returns {Promise<Object>} The Gemini API response as a JSON object.
 */
export async function sendToGeminiAPI(fileBlobOrInput) {
    const url = `/process_gemini`;
    // Call the API that handles Gemini processing
    const formData = new FormData();
    formData.append('file', fileBlobOrInput, 'certificate.png'); // The third argument is the filename
    try {
        console.log("Sending image to Gemini API via Python Sidecar...");
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            const errorDetail = await response.json();
            throw new Error(`[ ERROR ] Gemini API error: ${response.status} - ${errorDetail.detail}`);
        }
        const data = await response.json();
        console.log("[ SUCCESS ] Gemini API Result Received:", data);
        return data;
    } catch (error) {
        console.error('[ ERROR ] Error during Gemini API upload:', error);
    }  
}

/**
 * Checks if the Gemini API client is initialized on the server.
 * @returns {Promise<Object>} An object indicating if the Gemini API is available.
 */
export async function checkGeminiAPIAvailability() {
    const url = `/has_gemini`;
    try {
        console.log("Checking Gemini API availability...");
        const response = await fetch(url);
        if (!response.ok) {
            const errorDetail = await response.json();
            console.error(`[ ERROR ] Gemini API availability check error: ${response.status} - ${errorDetail.detail}`);
            alert("Error checking Gemini API availability. Please refresh the page and try again.");
        }
        const data = await response.json();
        console.log("[ SUCCESS ] Gemini API Availability:", data);
        return data;
    } catch (error) {
        console.error('[ ERROR ] Error during Gemini API availability check:', error);
        alert("Error checking Gemini API availability. Please refresh the page and try again.");
    }  
}