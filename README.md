# Local Image Viewer

A simple web-based image viewer application built with Flask that allows you to upload, view, and manage images locally.

## Features

- Upload images via drag-and-drop or file browser
- Gallery view with thumbnails
- Lightbox for full-size image viewing
- Detail view for individual images
- Delete images
- Download images
- Responsive design

## Requirements

- Python 3.6+
- Flask
- Pillow (PIL Fork)

## Installation

This project uses `uv` for dependency management. If you don't have `uv` installed, you can install it with:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then, set up the project:

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/local-image-viewer.git
   cd local-image-viewer
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   # Activate the virtual environment:
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   # source .venv/bin/activate
   
   # Install dependencies
   uv pip install flask pillow
   ```

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Use the "Upload Images" button to add images to your gallery.

## Project Structure

```
local-image-viewer/
├── app.py                  # Main Flask application
├── static/
│   ├── uploads/            # Stores uploaded images
│   └── thumbnails/         # Stores generated thumbnails
└── templates/
    ├── layout.html         # Base template
    ├── index.html          # Gallery view
    ├── upload.html         # Upload form
    └── image.html          # Single image view
```

## License

MIT 