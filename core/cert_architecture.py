from core.doctr_ocr import DoctrOCRWrapper       # Import DoctrOCRWrapper from the correct module
from core.paddle_ocr import PaddleOCRWrapper     # Import PaddleOCRWrapper from the correct module
from core.llm_post import LLMPostProcessor       # LLM post-processor
from core.preprocess import ImagePreProcessor    # Image pre-processor
from core.spacy_predict import NERPredictor      # NER predictor
# Libraries
from enum import Enum

class OCRModelType(Enum):   # Enum for OCR model selection
    DOCTR = "doctr"
    PADDLE = "paddle"

CATEGORIES = ["TYPE", "AWARDEE", "ROLE", "EVENT", "DATE", "LOCATION", "SIGNATORIES"]
class CertificateArchitecture:
    ocr_model: DoctrOCRWrapper | PaddleOCRWrapper
    llm_postprocessor: LLMPostProcessor
    image_preprocessor: ImagePreProcessor
    ner_predictor: NERPredictor
    def __init__(
        self,
        ocr_type=OCRModelType.PADDLE,
        with_llm_postprocessor=True,
        with_image_preprocessor=True,            
    ):
        """Initializes the CertificateArchitecture with specified OCR model, LLM post-processor, and NER predictor."""
        self.ocr_type = ocr_type
        self.with_llm_postprocessor = with_llm_postprocessor
        self.with_image_preprocessor = with_image_preprocessor
        match(ocr_type):
            case OCRModelType.DOCTR:
                self.ocr_model = DoctrOCRWrapper()
            case OCRModelType.PADDLE:
                self.ocr_model = PaddleOCRWrapper()
        if with_llm_postprocessor:
            self.llm_postprocessor = LLMPostProcessor()
        if with_image_preprocessor:
            self.image_preprocessor = ImagePreProcessor()
        self.ner_predictor = NERPredictor()
        pass

    def predict(self, image_path):
        """Runs the full prediction pipeline"""
        # Image preprocessing
        if self.with_image_preprocessor:
            print("[ MODEL ] Preprocessing image...")
            preprocessed_image = self.image_preprocessor.preprocess(image_path)
        else:
            preprocessed_image = image_path
        
        # OCR text extraction
        print("[ MODEL ] Running OCR model...")
        if self.ocr_type == OCRModelType.PADDLE:
            ocr_output = self.ocr_model.predict(preprocessed_image)
        elif self.ocr_type == OCRModelType.DOCTR:
            ocr_output, _, _ = self.ocr_model.predict(preprocessed_image)
        
        print("[ MODEL ] OCR Output:", ocr_output)
        # LLM post-processing
        if self.with_llm_postprocessor:
            print("[ MODEL ] Running LLM post-processing...")
            cleaned_text = self.llm_postprocessor.predict(ocr_output)
        else:
            cleaned_text = ocr_output
        
        print("[ MODEL ] Cleaned Text:", cleaned_text)
        # Entity extraction
        print("[ MODEL ] Running inference model...")
        prediction = self.ner_predictor.predict(cleaned_text)

        # Compile final results
        results = {}
        for category in CATEGORIES:
            results[category] = ", ".join(prediction.get(category, [])) if category == 'SIGNATORIES' and isinstance(prediction.get(category, []), list) else (prediction.get(category, [""])[0] if len(prediction.get(category, [])) > 0 else "")

        # Return results
        print(f"[ MODEL ] Final result:")
        
        results['IMAGE_PATH'] = image_path
        
        return results
    
    def switchModel(self, new_ocr_type: OCRModelType):
        """Switches the OCR model at runtime."""
        match(new_ocr_type):
            case OCRModelType.DOCTR:
                self.ocr_model = DoctrOCRWrapper()
            case OCRModelType.PADDLE:
                self.ocr_model = PaddleOCRWrapper()
        self.ocr_type = new_ocr_type