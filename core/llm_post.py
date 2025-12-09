import sys
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import re
import os
import traceback
from core.utils import resource_path

# --- CONFIGURATION ---
REPO_ID = "bartowski/Phi-3.5-mini-instruct-GGUF"
FILENAME = "Phi-3.5-mini-instruct-Q4_K_M.gguf"
LOCAL_MODEL_DIR = resource_path("models")
        
class LLMPostProcessor:
    def __init__(self):
        self.model_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir=LOCAL_MODEL_DIR,
            local_dir_use_symlinks=False
        )
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=4096,
            n_gpu_layers=-1, 
            verbose=False
        )
    def getPrompt(self, dirty_text):
        return f"""<|im_start|>system
You are a Certificate Restoration Engine. Your goal is to clean OCR text and format it for Named Entity Recognition (NER).

RULES:
1. **NO SUMMARIZATION:** Keep every detail. If the text says "Pursuant to Resolution No. 748-2024", keep it exactly like that.
2. **LANGUAGE SAFETY:** Do NOT translate Filipino words. Keep "Unibersidad ng Pilipinas", "Gawad", "Pagkilala" exactly as written.
3. **FIX SPACING & TYPOS:**
    - Fix run-together words: "CERTIFICATEOF" -> "CERTIFICATE OF", "FORAPPLIED" -> "FOR APPLIED".
    - Fix OCR typos: "TRATNING" -> "TRAINING", "Balinaa" -> "Bolinao", "succesofully" -> "successfully".
4. **PRESERVE DATES/LOCATIONS:** This certificate has TWO dates and TWO locations. Keep both clearly separated.
5. **RESTRUCTURE:** Reorder the information logically in a form of a certificate text:
    - Start with ORGANIZATION.
    - Then the CERTIFICATE TITLE.
    - Then AWARDEE.
    - Then EVENT details (keep specific dates matched to specific venues).
    - Then the DATE and LOCATION.
    - End with signatories and their TITLES. Example: "John Doe. Director.".
6. **FIX ARTIFACTS:** Remove random letters like "AD", "vsu", or broken lines from logos.
7. **SPELLING:** Correct any spelling mistakes in English words.
8. **NAME CLEANING (CRITICAL):** - Remove slashes (/), underscores (_), commas (,), or dots (.) that appear *inside* a name.
- **Example:** "Wenifel /SPochero" -> "Wenifel S. Pochero"
- **Example:** "EULOGIO /S.LABAO" -> "Eulogio S. Labao"
- **Example:** "J. /D. Cruz" -> "J. D. Cruz"
- Ensure Title Case for names (e.g., "WENIFEL" -> "Wenifel").
9. **NAME FORMATTING:** 
    - Ensure names and titles are properly capitalized: "leo cubillan" -> "Leo Cubillan", "WINIFEL PORPETCHO" -> "Wenifel Porpetcho".
    - Fix spacing in names: "DrWinifelP. Carmina" -> "Dr. Winifel P. Carmina". 
10. **DO NOT DUPLICATE NAMES OR DETAILS.** If a name or detail appears more than once, keep it only once in the cleaned text.
<|im_end|>
    
<|im_start|>user
Raw: "UNIV OF PHILIPPINES Award this CERTIFICATEOF COMPLETION to DR JANEAustenPHD. TRATNING ON DATA held on 1-2 Feb at Manila and 3-4 Feb at Cebu. Sgd Eulogio S/Tupa Assistant Producer DrWinifelP. Carmina Director"
<|im_end|>
<|im_start|>assistant
UNIVERSITY OF THE PHILIPPINES Awards this CERTIFICATE OF COMPLETION to Dr. Jane Austen Ph. D. for successfully completing the TRAINING ON DATA held on 1-2 Feb at Manila and 3-4 Feb at Cebu. Eulogio S. Tupa. Assistant Producer. Dr. Winifel P. Carmina. Director.
<|im_end|>

<|im_start|>user
Raw: "Unibersidad ng Pilipinas presents Ang Sertipiko ng Pagkilala ay iginagawad kay JUAN DELA CRUZ para sa kanyang kontribusyon. Ipinagkaloob ngayong Ika-13 ng Hunyo 2024 sa Bahay ng Alumni. Leo Cubillan Bise Presidente Angelo Jimenez Pangulo"
<|im_end|>
<|im_start|>assistant
Unibersidad ng Pilipinas presents Ang Sertipiko ng Pagkilala ay iginagawad kay Juan Dela Cruz para sa kanyang kontribusyon. Ipinagkaloob ngayong Ika-13 ng Hunyo 2024 sa Bahay ng Alumni. Leo Cubillan. Bise Presidente. Angelo Jimenez. Pangulo.
<|im_end|>

<|im_start|>user
Raw: "{dirty_text}"
<|im_end|>
<|im_start|>assistant
"""
        
    def predict(self, dirty_text):
        prompt = self.getPrompt(dirty_text)
        output = self.llm(
            prompt, 
            max_tokens=1024,
            stop=["<|im_end|>"], 
            echo=False,
            temperature=0.3, 
            repeat_penalty=1.1
        )
        
        result = output['choices'][0]['text'].strip()
        return re.sub(r'\s+', ' ', result)