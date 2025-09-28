import os
import shutil
import re
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import pathlib

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
THUMBNAILS_FOLDER = os.path.join('static', 'thumbnails')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAILS_FOLDER'] = THUMBNAILS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAILS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_thumbnail(image_path, thumbnail_path, size=(200, 200)):
    """Create a thumbnail for an image"""
    try:
        img = Image.open(image_path)
        img.thumbnail(size)
        img.save(thumbnail_path)
    except Exception as e:
        print(f"Error creating thumbnail: {e}")

def get_image_dimensions(image_path):
    """Get the width and height of an image"""
    try:
        with Image.open(image_path) as img:
            return img.width, img.height
    except Exception as e:
        print(f"Error getting image dimensions: {e}")
        return 800, 600  # Default dimensions if unable to determine

def get_folders_in_path(path):
    """Get all folders in the given path"""
    folders = []
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], path) if path else app.config['UPLOAD_FOLDER']
    
    if os.path.exists(full_path):
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                # Count images in this folder
                image_count = count_images_in_folder(os.path.join(path, item) if path else item)
                folders.append({
                    'name': item,
                    'path': os.path.join(path, item).replace('\\', '/') if path else item,
                    'image_count': image_count
                })
    
    return folders

def count_images_in_folder(folder_path):
    """Count images in a folder recursively"""
    count = 0
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_path) if folder_path else app.config['UPLOAD_FOLDER']
    
    if os.path.exists(full_path):
        for root, dirs, files in os.walk(full_path):
            for file in files:
                if allowed_file(file):
                    count += 1
    
    return count

def get_breadcrumbs(current_path):
    """Generate breadcrumb navigation"""
    breadcrumbs = [{'name': 'Gallery', 'path': ''}]
    
    if current_path:
        parts = current_path.split('/')
        path = ''
        for part in parts:
            path = os.path.join(path, part).replace('\\', '/') if path else part
            breadcrumbs.append({'name': part, 'path': path})
    
    return breadcrumbs

def validate_folder_name(name):
    """Validate folder name"""
    if not name or not name.strip():
        return False, "Folder name cannot be empty"
    
    name = name.strip()
    
    if len(name) > 100:
        return False, "Folder name too long (max 100 characters)"
    
    # Check for invalid characters
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        return False, "Folder name can only contain letters, numbers, spaces, hyphens, and underscores"
    
    # Check for reserved names
    reserved_names = ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9']
    if name.lower() in reserved_names:
        return False, "This folder name is reserved by the system"
    
    return True, ""

@app.route('/')
@app.route('/folder/<path:folder_path>')
def index(folder_path=''):
    """Home page - displays all images in a grid with folder support"""
    images = []
    
    # Determine the current folder path
    current_path = folder_path.strip('/') if folder_path else ''
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], current_path) if current_path else app.config['UPLOAD_FOLDER']
    
    # Ensure the path exists
    if not os.path.exists(full_path):
        flash('Folder not found', 'error')
        return redirect(url_for('index'))
    
    # Get folders in current path
    folders = get_folders_in_path(current_path)
    
    # Get images from the current folder (not recursive)
    if os.path.exists(full_path):
        for filename in os.listdir(full_path):
            file_path = os.path.join(full_path, filename)
            if os.path.isfile(file_path) and allowed_file(filename):
                # Create relative paths for thumbnails
                relative_image_path = os.path.join(current_path, filename).replace('\\', '/') if current_path else filename
                thumbnail_filename = relative_image_path.replace('/', '_')
                
                thumbnail_path = os.path.join(app.config['THUMBNAILS_FOLDER'], thumbnail_filename)
                
                # Create thumbnail if it doesn't exist
                if not os.path.exists(thumbnail_path):
                    create_thumbnail(file_path, thumbnail_path)

                # Get image dimensions for PhotoSwipe
                width, height = get_image_dimensions(file_path)

                images.append({
                    'filename': filename,
                    'relative_path': relative_image_path,
                    'thumbnail': os.path.join('thumbnails', thumbnail_filename).replace('\\', '/'),
                    'full_image': os.path.join('uploads', relative_image_path).replace('\\', '/'),
                    'width': width,
                    'height': height,
                    'folder': current_path.split('/')[-1] if current_path else None
                })

    # Generate breadcrumbs
    breadcrumbs = get_breadcrumbs(current_path)
    
    return render_template('index.html', 
                         images=images, 
                         folders=folders,
                         current_path=current_path,
                         breadcrumbs=breadcrumbs)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file uploads with folder support"""
    # Get folder path from URL parameter or form data
    folder_path = request.args.get('folder', '').strip('/')
    
    if request.method == 'POST':
        # Also check for folder_path in form data (from hidden field)
        form_folder_path = request.form.get('folder_path', '').strip('/')
        if form_folder_path:
            folder_path = form_folder_path
            
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No files selected', 'error')
            # Preserve folder parameter in redirect
            if folder_path:
                return redirect(url_for('upload_file', folder=folder_path))
            else:
                return redirect(url_for('upload_file'))

        files = request.files.getlist('file')
        uploaded_count = 0

        # Determine upload directory
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], folder_path) if folder_path else app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)

        for file in files:
            if file.filename == '':
                continue

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)

                # Create thumbnail with proper naming for folder structure
                relative_path = os.path.join(folder_path, filename).replace('\\', '/') if folder_path else filename
                thumbnail_filename = relative_path.replace('/', '_')
                thumbnail_path = os.path.join(app.config['THUMBNAILS_FOLDER'], thumbnail_filename)
                create_thumbnail(file_path, thumbnail_path)
                
                uploaded_count += 1
    
        if uploaded_count > 0:
                flash(f'Successfully uploaded {uploaded_count} image(s)', 'success')
        else:
            flash('No valid images were uploaded', 'error')

        # Redirect back to the folder
        if folder_path:
            return redirect(url_for('index', folder_path=folder_path))
        else:
            return redirect(url_for('index'))

    return render_template('upload.html', current_path=folder_path)

@app.route('/image/<path:filename>')
def view_image(filename):
    """View a single image in detail"""
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    width, height = get_image_dimensions(image_path)

    return render_template('image.html', filename=filename, width=width, height=height)

@app.route('/delete/<path:filename>')
def delete_image(filename):
    """Delete an image with folder support"""
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Create thumbnail filename for folder structure
    thumbnail_filename = filename.replace('/', '_')
    thumbnail_path = os.path.join(app.config['THUMBNAILS_FOLDER'], thumbnail_filename)

    if os.path.exists(image_path):
        os.remove(image_path)
        flash('Image deleted successfully', 'success')

    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

    # Redirect back to the appropriate folder
    folder_path = '/'.join(filename.split('/')[:-1]) if '/' in filename else ''
    if folder_path:
        return redirect(url_for('index', folder_path=folder_path))
    else:
        return redirect(url_for('index'))

@app.route('/create_folder', methods=['POST'])
def create_folder():
    """Create a new folder"""
    folder_name = request.form.get('folder_name', '').strip()
    current_path = request.form.get('current_path', '').strip()
    
    # Validate folder name
    is_valid, error_message = validate_folder_name(folder_name)
    if not is_valid:
        flash(error_message, 'error')
        if current_path:
            return redirect(url_for('index', folder_path=current_path))
        else:
            return redirect(url_for('index'))
    
    # Create the full path
    if current_path:
        new_folder_path = os.path.join(current_path, folder_name)
    else:
        new_folder_path = folder_name
    
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], new_folder_path)
    
    # Check if folder already exists
    if os.path.exists(full_path):
        flash('A folder with this name already exists', 'error')
    else:
        try:
            os.makedirs(full_path, exist_ok=True)
            flash(f'Folder "{folder_name}" created successfully', 'success')
        except Exception as e:
            flash(f'Error creating folder: {str(e)}', 'error')
    
    # Redirect back to current path
    if current_path:
        return redirect(url_for('index', folder_path=current_path))
    else:
        return redirect(url_for('index'))

@app.route('/delete_folder/<path:folder_path>')
def delete_folder(folder_path):
    """Delete a folder and all its contents"""
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_path)
    
    if os.path.exists(full_path) and os.path.isdir(full_path):
        try:
            # Remove all thumbnails for images in this folder
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    if allowed_file(file):
                        relative_path = os.path.relpath(os.path.join(root, file), app.config['UPLOAD_FOLDER'])
                        thumbnail_filename = relative_path.replace('\\', '/').replace('/', '_')
                        thumbnail_path = os.path.join(app.config['THUMBNAILS_FOLDER'], thumbnail_filename)
                        if os.path.exists(thumbnail_path):
                            os.remove(thumbnail_path)
            
            # Remove the folder
            shutil.rmtree(full_path)
            flash(f'Folder deleted successfully', 'success')
        except Exception as e:
            flash(f'Error deleting folder: {str(e)}', 'error')
    else:
        flash('Folder not found', 'error')
    
    # Redirect to parent folder
    parent_path = '/'.join(folder_path.split('/')[:-1]) if '/' in folder_path else ''
    if parent_path:
        return redirect(url_for('index', folder_path=parent_path))
    else:
        return redirect(url_for('index'))

@app.route('/api/folder/validate', methods=['POST'])
def validate_folder_api():
    """API endpoint for real-time folder name validation"""
    data = request.get_json()
    folder_name = data.get('folder_name', '').strip()
    current_path = data.get('current_path', '').strip()
    
    # Validate folder name
    is_valid, error_message = validate_folder_name(folder_name)
    
    if is_valid:
        # Check if folder already exists
        if current_path:
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], current_path, folder_name)
        else:
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        
        if os.path.exists(full_path):
            is_valid = False
            error_message = "A folder with this name already exists"
    
    return jsonify({
        'valid': is_valid,
        'message': error_message
    })

@app.route('/api/images/all')
@app.route('/api/images/all/<path:folder_path>')
def get_all_images_api(folder_path=''):
    """API endpoint to get all images including subfolders"""
    images = []
    base_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_path) if folder_path else app.config['UPLOAD_FOLDER']
    
    if os.path.exists(base_path):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if allowed_file(file):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, app.config['UPLOAD_FOLDER']).replace('\\', '/')
                    
                    # Get image dimensions
                    width, height = get_image_dimensions(file_path)
                    
                    # Create thumbnail filename
                    thumbnail_filename = relative_path.replace('/', '_')
                    
                    images.append({
                        'filename': file,
                        'relative_path': relative_path,
                        'thumbnail': os.path.join('thumbnails', thumbnail_filename).replace('\\', '/'),
                        'full_image': os.path.join('uploads', relative_path).replace('\\', '/'),
                        'width': width,
                        'height': height,
                        'folder': os.path.dirname(relative_path) if os.path.dirname(relative_path) else None
                    })
    
    return jsonify({
        'images': images,
        'count': len(images)
    })

if __name__ == '__main__':
    app.run(debug=False)
