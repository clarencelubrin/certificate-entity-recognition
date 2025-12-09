
# 🖼️ Certificate Entity Recognition

This web application is designed to recognize and extract critical data entities (like holder name, issue date, certificate ID, etc.) from uploaded certificate images. It is built to automate the manual process of data entry, significantly improving efficiency and accuracy in handling large volumes of certificates.

The application is deployed on a FastAPI server and uses a modern, high-performance architecture written entirely in Python.


## ⚙️ Technology Stack

**Backend** Python and FastAPI

**Frontend** HTML, CSS, JavaScript

**Computer Vision** OpenCV

**Text Extraction (OCR)** DocTR and PaddleOCR

**Entity Recognition (NER)** SpaCy

**Supported Operating System** Windows


## 🛠️ Installation
* Download the [Certificate-Entity-Recognition-v1.0.0.zip](https://github.com/clarencelubrin/certificate-entity-recognition/releases/tag/v1.0.0) archive file.
* Extract the Certificate-Entity-Recognition-v1.0.0.zip to a file destination of your choice.
* Run the executable file. (Note: Running the local model for the first time may take a while since it downloads the LLM model for the postprocessing).
    

## 📦 Architecture

![alt text](https://github.com/clarencelubrin/certificate-entity-recognition/blob/main/markup-img/arch.jpg)

The system follows a standard pipeline combining **Computer Vision** and **Natural Language Processing (NLP)** techniques to transform an unstructured image into structured data.

1. **Input and Server Interface**

A user uploads a certificate image via the Web Application Frontend. The FastAPI server receives the image and initiates the processing workflow.

2. **Image Pre-processing**

OpenCV handles the image: It cleans the image, corrects distortions (deskewing), and enhances clarity to maximize OCR accuracy.

3. **Object Character Recognition and Text Extraction**
OCR engine then reads the cleaned image, converting the visual text into a large block of unstructured text data.

4. **LLM Post-processing**
The LLM handles the OCR raw text. It cleans the noisy extracted text to increase NER accuracy.

3. **Entity Recognition**

A fine-tuned Named Entity Recognition (NER) SpaCy model identify and tag relevant fields.

4. **Output**
The application compiles all the recognized entities into a Structured Output format (typically JSON), which is then returned by the FastAPI server to the user.
## Configuration

You can change the configuration (model.conf) of your local model.
```python
OCR_MODEL               = paddle      # Either doctr or paddle
HAS_LLM_POSTPROCESSING  = True        # Is LLM postprocessing included
HAS_IMAGE_PREPROCESSING = True        # Is Image preprocessing included
```
If you want to use Google Gemini Flash 2.5, you can provide your own Gemini API key:
```python
GEMINI_API_KEY          =             # Gemini API key (optional)
```
FastAPI backend server configuration:
```python
WORKERS                 = 1           # Number of workers for FastAPI
HOST                    = 127.0.0.0   # Host IP address
PORT                    = 800         # Host port number
```
