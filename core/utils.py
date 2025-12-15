import os
import sys
from pathlib import Path

def read_config(config_path="config.conf"):
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    else:
        # Create a default config file if it doesn't exist
        with open(config_path, "w") as f:
            f.write("# Local Model Configuration\n")
            f.write("OCR_MODEL=paddle\n")
            f.write("NER_MODEL=spacy\n")
            f.write("HAS_LLM_POSTPROCESSING=True\n")
            f.write("HAS_IMAGE_PREPROCESSING=True\n")
            f.write("\n# Gemini API Configuration\n")
            f.write("GEMINI_MODEL=gemini-2.5-flash\n")
            f.write("GEMINI_API=\n")
            f.write("\n# Server Configuration\n")
            f.write("WORKERS=1\n")
            f.write("HOST=localhost\n")
            f.write("PORT=8000\n")
        config = {
            "GEMINI_API": "",
            "OCR_MODEL": "paddle",
            "HAS_LLM_POSTPROCESSING": "True",
            "HAS_IMAGE_PREPROCESSING": "True",
            "WORKERS": "1",
            "HOST": "localhost",
            "PORT": "8000"
        }
    return config

def resource_path(relative_path: str) -> Path:
    """
    Gets the absolute path to a resource, adjusting for the core/utils.py nesting 
    to find files relative to the 'certificate_app' root.
    """
    # PyInstaller/Briefcase Packaged Environment Check
    if hasattr(sys, '_MEIPASS'):
        # In a packaged app, resources are flattened into the _MEIPASS temp directory.
        base_path = Path(sys._MEIPASS)
    
    # Development/Briefcase Dev Environment Check
    else:
        # Get the directory where utils.py lives (the 'core' folder)
        try:
            # Resolves to: /src/certificate_app/core
            core_dir = Path(__file__).resolve().parent 
        except NameError:
            core_dir = Path.cwd()
            
        # Move UP one directory to reach the application root (certificate_app).
        # This resolves to: /src/certificate_app
        base_path = core_dir.parent 
            
    # Join the base path and the relative path
    # Example return: /src/certificate_app/static
    return base_path / relative_path
