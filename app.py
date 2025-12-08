# API Endpoint for Tauri application
# Using FastAPI to handle OCR requests
import os

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware # Import the middleware
from fastapi.staticfiles import StaticFiles
import uvicorn
# Utilities
from io import BytesIO
import PIL.Image as Image
import tempfile
from pydantic import BaseModel, Field
from typing import Annotated, List
# Core modules
from core.utils import read_config, resource_path
from core.cert_architecture import CertificateArchitecture, OCRModelType
# Gemini API
from google import genai
from google.genai import types

# Load configuration
config = read_config()
GEMINI_API_KEY          = config.get("GEMINI_API", "")
OCR_MODEL               = config.get("OCR_MODEL", "paddle").lower()
HAS_LLM_POSTPROCESSING  = config.get("HAS_LLM_POSTPROCESSING", "True").lower() == "true"
HAS_IMAGE_PREPROCESSING = config.get("HAS_IMAGE_PREPROCESSING", "True").lower() == "true"
WORKERS                 = int(config.get("WORKERS", "1"))
HOST                    = config.get("HOST", "127.0.0.1")
PORT                    = int(config.get("PORT", "8000"))

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
cert_architecture = None

STATIC_DIR = resource_path("static")
TEMPLATES_DIR = resource_path("templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def load_model_once():
    """Simulates loading a large model that takes time."""
    global cert_architecture
    if cert_architecture is None:
        print("[ SERVER ] Loading heavy model... (This runs only once)")
        cert_architecture = CertificateArchitecture(
            ocr_type=OCRModelType.DOCTR if OCR_MODEL == "doctr" else OCRModelType.PADDLE,
            with_image_preprocessor=HAS_IMAGE_PREPROCESSING,
            with_llm_postprocessor=HAS_LLM_POSTPROCESSING
        )
        print("[ SERVER ] Model Loaded!")
    return cert_architecture
    
# Endpoint to serve the main page
@app.get("/", tags=["Pages"])
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "My FastAPI App"})

@app.post("/process_ocr")
async def process_ocr(
    image_file: UploadFile = File(...)
):
    model = load_model_once() 
    try:
        image_bytes = await image_file.read()
        image = Image.open(BytesIO(image_bytes))
        # Save image to a temporary path in the computer then send the path to the model
        temp_path = tempfile.gettempdir()
        image_path = os.path.join(temp_path, image_file.filename)
        image.save(image_path)
        extracted_data = model.predict(image_path)
        return {
            "status": "success",
            "file_name": image_file.filename,
            "file_size_bytes": len(image_bytes),
            "extracted_text": extracted_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

# GEMINI API
GEMINI_CLIENT = None
if GEMINI_API_KEY:
    try:
        # Client is initialized using the GEMINI_API_KEY environment variable
        GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[ SERVER ] No GEMINI API Key found or error initializing Gemini Client: {e}")
    
class DocumentInfo(BaseModel):
    """The main Pydantic model for the final JSON response."""
    TYPE: str = Field(description="The type of document or item (e.g., 'Certificate of Participation', 'Award', 'Diploma', 'Contract').")
    AWARDEE: str = Field(description="The name of the person or entity receiving the award/document.")
    ROLE: str = Field(description="The role or capacity in which the awardee received the item (e.g., 'Speaker', 'Participant', 'Winner').")
    EVENT: str = Field(description="The name of the event, conference, or program.")
    DATE: str = Field(description="The date the document was issued or the event took place (retain the formatting of the date).")
    LOCATION: str = Field(description="The location (retain the complete address stated in the certificate) where the event or issuance occurred.")
    SIGNATORIES: List[str] = Field(description="A list of the names of the people who signed the document. Extract only the names, not titles or roles.")

@app.get("/has_gemini")
async def has_gemini():
    """Endpoint to check if Gemini API client is initialized."""
    return {"has_gemini_api": GEMINI_CLIENT is not None}

@app.post(
    "/process_gemini",
    response_model=DocumentInfo,
    summary="Upload image and extract key document info as JSON"
)
async def extract_info(
    # FastAPI's UploadFile handles the incoming file efficiently
    file: Annotated[UploadFile, File(description="An image file (e.g., JPG, PNG) of a document.")]
):
    """
    Accepts an image file, sends it to the Gemini API, and returns
    structured JSON data based on the DocumentInfo schema.
    """
    if GEMINI_CLIENT is None:
        raise HTTPException(
            status_code=503, 
            detail="Gemini API client is not initialized. Please check the server configuration."
        )
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload an image file (e.g., JPEG, PNG)."
        )

    try:
        # Read the file content as bytes
        image_bytes = await file.read()
        mime_type = file.content_type

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )

        # The prompt is updated to reinforce the requirement for names only
        prompt = (
            "Analyze the provided image. This image is a document (like a certificate or award). "
            "Extract all the requested key information into a single JSON object as per the defined schema. "
            "For the SIGNATORIES field, **only provide the names** of the people who signed. "
            "If a field's value is not clearly present in the image, use 'N/A' for that value."
        )
        print("[ SERVER ] Sending request to Gemini API...")
        response = GEMINI_CLIENT.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image_part, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                # The Pydantic model is passed directly as the schema
                response_schema=DocumentInfo, 
            ),
        )
        print("[ SERVER ] Received response from Gemini API.")
        document_info_instance = DocumentInfo.model_validate_json(response.text)
        document_info_dict = document_info_instance.model_dump()
        print(f"[ SERVER ] Extracted Document Info: {document_info_dict}")
        return document_info_dict

    except Exception as e:
        # Log the error for debugging
        print(f"Gemini API Error: {e}")
        # Return a generic error to the client
        raise HTTPException(
            status_code=500, 
            detail="An error occurred during Gemini API processing."
        )

def main():
    print("[ SERVER ] Starting FastAPI server...")
    print("[ SERVER ] Model Configuration:")
    print(f" - OCR Model: {OCR_MODEL}")
    print(f" - LLM Post-Processing: {HAS_LLM_POSTPROCESSING}")
    print(f" - Image Pre-Processing: {HAS_IMAGE_PREPROCESSING}")
    print(f" - Gemini Client Initialized: {GEMINI_CLIENT is not None}")
    print(f" - Workers: {WORKERS}")
    uvicorn.run(app, host=HOST, port=PORT, workers=WORKERS, log_level="debug")
    
if __name__ == "__main__":
    main()