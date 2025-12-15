from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import re
import traceback
from core.utils import resource_path

# --- CONFIGURATION FOR QWEN 2.5 3B ---
# We use the official Qwen GGUF repo or a reliable community one (Bartowski is highly reliable)
REPO_ID = "Qwen/Qwen2.5-3B-Instruct-GGUF"
FILENAME = "qwen2.5-3b-instruct-q4_k_m.gguf"

LOCAL_MODEL_DIR = resource_path("models")

class LLMPostProcessor:
    def __init__(self):
        print(f"Loading model: {FILENAME}...")
        self.model_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir=LOCAL_MODEL_DIR,
            local_dir_use_symlinks=False
        )
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=4096,           # Context window
            n_gpu_layers=-1,      # -1 = Offload all to GPU if available, otherwise CPU
            verbose=False
        )

    def getPromptQwen(self, dirty_text):
        """
        Qwen 2.5 uses the ChatML format:
        <|im_start|>system...<|im_end|><|im_start|>user...<|im_end|><|im_start|>assistant
        """
        return f"""<|im_start|>system
You are an expert OCR post-processing assistant for English and Tagalog text.
Your task is to correct spelling errors, fix broken words, and repair grammar.

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
Raw Text:
"{dirty_text}"
<|im_end|>
<|im_start|>assistant
"""

    def predict(self, dirty_text):
        try:
            # Switch to the Qwen prompt generator
            prompt = self.getPromptQwen(dirty_text)
            
            output = self.llm(
                prompt,
                max_tokens=2048,        # Increased slightly for longer certificates
                stop=["<|im_end|>"],    # Qwen's specific stop token
                echo=False,
                temperature=0.1,        # Low temp = more deterministic/faithful to original text
                top_p=0.9,
                repeat_penalty=1.1      # Prevents loops
            )

            result = output['choices'][0]['text'].strip()
            
            # Post-cleaning: Collapse multiple spaces into one
            return re.sub(r'\s+', ' ', result)

        except Exception as e:
            print(f"Error during prediction: {e}")
            traceback.print_exc()
            return dirty_text # Return original if failure
        
