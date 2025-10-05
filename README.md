# Image Viewer

Flask-based image viewer with folder support and thumbnail generation.

## Quick Start with UV

### 1. Install UV (Windows)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Setup Environment
```bash
# Create virtual environment
uv venv

# Activate it (Windows)
.venv\Scripts\activate
```

### 3. Install Dependencies

**Option A: From pyproject.toml (Recommended)**
```bash
uv pip install -e .
```

**Option B: Direct install**
```bash
uv pip install flask pillow werkzeug
```

### 4. Run the App
```bash
python app.py
```

Open browser: **http://127.0.0.1:5000**

---

## Alternative: Use Setup Script
```bash
setup.bat
run.bat
```

## Features
- Upload & organize images in folders
- Thumbnail generation
- Lightbox gallery view
- Folder navigation with breadcrumbs
- Drag-and-drop upload support 