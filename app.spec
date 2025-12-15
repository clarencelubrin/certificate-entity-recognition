# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# ========================================================
# USER CONFIGURATION
# ========================================================
APP_NAME = 'CertificateEntityRecognition'  # <--- RENAME YOUR EXECUTABLE HERE
ENABLE_CONSOLE = True  # <--- Set to True for debug window, False for GUI only
# ========================================================

# --------------------------------------------------------
# 1. HEAVY DEPENDENCY ANALYSIS
# These packages from your requirements.txt are known to 
# fail in PyInstaller unless fully collected.
# --------------------------------------------------------
packages_to_collect = [
    # --- Paddle Stack (The source of your current crash) ---
    'paddle', 'paddleocr', 'paddlex', 'pyclipper', 
    'shapely', 'skimage', 'imgaug', 'lmdb',

    # --- PyTorch & AI Stack ---
    'torch', 'torchvision', 'numpy', 'scipy', 'pandas',
    'onnx', 'onnxruntime', 'networkx',

    # --- HuggingFace / LLM Stack ---
    'transformers', 'tokenizers', 'huggingface_hub', 
    'safetensors', 'llama_cpp', 'sentencepiece',

    # --- SpaCy Stack (Very fragile) ---
    'spacy', 'spacy_transformers', 'thinc', 'srsly', 
    'cymem', 'preshed', 'blis', 'murmurhash', 
    'catalogue', 'confection', 'wasabi', 'weasel', 
    'langcodes',

    # --- Web Server Stack ---
    'uvicorn', 'fastapi', 'starlette', 'anyio', 
    'httpcore', 'httpx', 'python_multipart', 'websockets',

    # --- Document/Image Processing ---
    'cv2',             # opencv-python
    'pypdfium2',       # PDF processing
    'PIL',             # pillow
    'doctr',           # python-doctr
    'rapidfuzz',       # string matching
    
    # --- Google/Cloud SDKs ---
    'google.generativeai', 'google.auth', 'grpc',
]

# Initialize containers
tmp_binaries = []
tmp_datas = []
tmp_hiddenimports = []

# Collect everything
print(f"Collecting resources for {len(packages_to_collect)} complex libraries...")
for package in packages_to_collect:
    try:
        # collect_all gathers datas, binaries, and hiddenimports
        c_datas, c_binaries, c_hiddenimports = collect_all(package)
        tmp_datas.extend(c_datas)
        tmp_binaries.extend(c_binaries)
        tmp_hiddenimports.extend(c_hiddenimports)
    except Exception as e:
        # Some packages might be missing optional sub-deps; just warn and continue
        print(f"(!) Warning: Could not collect '{package}'. It might not be installed. Details: {e}")

# --------------------------------------------------------
# 2. ANALYSIS
# --------------------------------------------------------
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=tmp_binaries,
    datas=tmp_datas + [
        ('core', 'core'), 
        ('models', 'models'), 
        ('static', 'static'), 
        ('templates', 'templates')
    ],
    hiddenimports=tmp_hiddenimports + [
        # Explicit hidden imports often missed by hooks
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'engineio.async_drivers.threading',
        'sklearn.utils._cython_blas',
        'sklearn.neighbors.typedefs',
        'sklearn.neighbors.quad_tree',
        'sklearn.tree',
        'sklearn.tree._utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# --------------------------------------------------------
# 3. EXE (The Launcher)
# --------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [], 
    exclude_binaries=True, # MUST be True for Onedir builds
    name=APP_NAME,         # Uses the name you set at the top
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=ENABLE_CONSOLE, # Uses the setting from the top
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# --------------------------------------------------------
# 4. COLLECT (The Output Folder)
# --------------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,         # Uses the name you set at the top
)