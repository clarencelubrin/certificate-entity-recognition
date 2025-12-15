from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from core.utils import resource_path
import json
import re

# --- CONFIGURATION ---
REPO_ID = "bartowski/Qwen2.5-7B-Instruct-GGUF"
FILENAME = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
LOCAL_MODEL_DIR = resource_path("models")

class LLMKIEPredictor:
    def __init__(self):
        print(f"Loading Model: {FILENAME}...")
        self.model_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir=LOCAL_MODEL_DIR,
            local_dir_use_symlinks=False
        )
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=8192,
            n_gpu_layers=-1,
            verbose=False
        )

    def extract_json_block(self, text):
        match = re.search(r"\{[\s\S]*\}", text)
        return match.group(0) if match else None

    def predict(self, ocr_text: str):
        # --- IMPROVED PROMPT STRATEGY ---
        # 1. Added explicit instruction to exclude the Awardee from Signatories.
        # 2. Added specific examples of what NOT to include (Project names).
        # 3. Forced OCR correction for "IRAINING".
        
        prompt = f"""<|im_start|>system
You are a Document Entity Extraction Engine. 
Your task is to parse messy OCR text and return a cleaned JSON object.

### CRITICAL RULES
1. **OCR REPAIR:** You MUST fix typos. 
   - "IRAINING" -> "TRAINING"
   - "0Santiago" -> "Santiago"
   - "Mani1a" -> "Manila"
   
2. **SIGNATORIES (STRICT):**
   - **Exclude the Awardee:** The person receiving the certificate CANNOT be a signatory.
   - **Exclude Organizations:** Do not list "Phil-Li DAR", "UP Diliman", or "LIDAR" as signatories.
   - **Include Honorifics:** Keep "Dr.", "Engr.", "M.Sc." in the name string.
   - **Format:** If the text is "Ayin M. Tamondong, M.Sc. Project Leader", the Signatory is "Ayin M. Tamondong, M.Sc." and the Title is "Project Leader".

3. **N/A HANDLING:** 
   - If any field is missing or cannot be determined, use "N/A" for strings and an empty list for arrays.

### JSON SCHEMA
{{
  "TYPE": "Type of document (e.g., Certificate of Participation)",
  "AWARDEE": "Full name of the recipient",
  "ROLE": "Role of the awardee (e.g., Speaker, Participant)",
  "EVENT": "Name of the event (Corrected spelling)",
  "DATE": "Date of the event",
  "LOCATION": "Venue/Location",
  "SIGNATORIES": ["List of names (Person Only)."],
  "SIGNATORY_TITLES": ["List of titles corresponding to the signatories."]
}}
<|im_end|>
<|im_start|>user
Raw OCR Text:
"{ocr_text}"
<|im_end|>
<|im_start|>assistant
"""
        
        response = self.llm(
            prompt,
            max_tokens=1024,
            temperature=0.1,  # Keep low to force strict adherence
            stop=["<|im_end|>"],
            echo=False
        )

        output_text = response["choices"][0]["text"].strip()

        # Parse JSON
        json_text = self.extract_json_block(output_text)
        
        if json_text:
            try:
                data = json.loads(json_text)
                # Enforce List format
                for key in data:
                    if not isinstance(data[key], list):
                        val = data[key]
                        data[key] = [] if val in ["N/A", ""] else [val]
                return data
            except json.JSONDecodeError:
                return {"error": "JSON parse failed", "raw": output_text}
        
        return {"error": "No JSON found", "raw": output_text}