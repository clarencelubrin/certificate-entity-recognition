from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
from unittest.mock import patch
from transformers.dynamic_module_utils import check_imports


class LLMOCRWrapper:
    def __init__(self):
        self.model_id = "microsoft/Florence-2-large"
        # Apply the fix specifically during the load
        with patch("transformers.dynamic_module_utils.check_imports", self.fixed_check_imports):
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                trust_remote_code=True
            ).to("cpu")

        self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)

    def fixed_check_imports(self, filename):
        try:
            return check_imports(filename)
        except ImportError as e:
            if "flash_attn" in str(e):
                # These are the files Florence-2 needs to load locally
                return ["configuration_florence2", "processing_florence2", "modeling_florence2"]
            raise e

    def predict(self, image_path):
        image = Image.open(image_path).convert("RGB")

        # Define Prompt
        prompt = "<OCR_WITH_REGION>"

        print("Processing image...")
        inputs = self.processor(text=prompt, images=image, return_tensors="pt")

        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            do_sample=False,
            num_beams=3,
        )

        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = self.processor.post_process_generation(
            generated_text,
            task=prompt,
            image_size=(image.width, image.height)
        )

        if '<OCR_WITH_REGION>' in parsed_answer:
            lines = parsed_answer['<OCR_WITH_REGION>']['labels']
            return lines.replace('<line>', '').replace('</line>', '\n').strip()
        else:
            print("No text regions found.")
            return ""