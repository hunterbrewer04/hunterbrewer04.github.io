from flask import Flask, request, render_template, send_file
import os
import pyheif
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
ALLOWED_EXTENSIONS = {'heic'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def heic_to_jpg(input_folder, output_folder):
    """
    Converts all HEIC images in the input_folder to JPG and saves them to the output_folder.
    """
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.heic'):
            heic_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.jpg")

            try:
                # Read the HEIC file
                heif_file = pyheif.read(heic_path)

                # Convert HEIC to a Pillow Image object
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                )

                # Save the image as a JPG
                image.save(output_path, "JPEG", quality=95)  # Quality set to 95 for high-quality output
                print(f"Converted: {filename} -> {output_path}")

            except Exception as e:
                print(f"Failed to convert {filename}: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Convert the file
        heic_to_jpg(app.config['UPLOAD_FOLDER'], app.config['CONVERTED_FOLDER'])

        # Path to the converted file
        converted_filename = filename.rsplit('.', 1)[0] + '.jpg'
        converted_filepath = os.path.join(app.config['CONVERTED_FOLDER'], converted_filename)

        # Serve the converted file
        return send_file(converted_filepath, as_attachment=True)

    return "File not allowed", 400

if __name__ == "__main__":
    app.run(debug=True)
