import os
from PIL import Image
import google.generativeai as genai
from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Store your API key as an environment variable
os.environ['GOOGLE_API_KEY'] = "AIzaSyBHv0lHPwN8nsCEkgj7r_AB5_xsg7YVfBk"

# Now retrieve the stored API key
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Configure your GenAI library
genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def process_image_and_generate_content(image_path):
    try:
        # Open the image
        img = Image.open(image_path)

        # Initialize the generative model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Generate content from the image
        response = model.generate_content(img)
        content = response.text

        # Additional processing
        response = model.generate_content(["Give me all food item names with calories ", img], stream=True)
        response.resolve()
        additional_content = response.text

        return content, additional_content

    except Exception as e:
        return f"An error occurred: {e}", None

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            content, additional_content = process_image_and_generate_content(file_path)
            preview_image_url = url_for('uploaded_file', filename=filename)
            return render_template_string(TEMPLATE, content=content, additional_content=additional_content, preview_image_url=preview_image_url)
    return render_template_string(TEMPLATE)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

TEMPLATE = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Image Content Generator</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
      * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
          font-family: 'Arial', sans-serif;
      }
      body {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          background: linear-gradient(45deg, #ff6f61, #deff8a, #61a3ff);
          background-size: 300% 300%;
          animation: gradient 15s ease infinite;
      }
      @keyframes gradient {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
      }
      .container {
          text-align: center;
          background: rgba(255, 255, 255, 0.2); /* Semi-transparent background */
          border-radius: 15px;
          padding: 20px;
          width: 90%;
          max-width: 600px;
          box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
      }
      .image-preview {
          text-align: center;
          margin-bottom: 20px;
      }
      .image-preview img {
          max-width: 100%;
          max-height: 400px; /* Limit height for large images */
          border-radius: 8px;
          box-shadow: 0 0 10px rgba(0,0,0,0.1); /* Shadow for image */
      }
      h1 {
          color: #ffffff;
          margin-bottom: 20px;
          font-size: 2.5em;
          text-shadow: 2px 2px 4px #000000;
      }
      .form-group label {
          color: #ffffff;
      }
      .form-group input {
          padding: 10px;
          font-size: 1em;
          border: none;
          border-radius: 5px;
      }
      .btn-primary {
          padding: 10px 20px;
          font-size: 1em;
          color: #ffffff;
          background-color: #61a3ff;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          transition: background-color 0.3s ease;
      }
      .btn-primary:hover {
          background-color: #5194e3;
      }
      .btn {
          margin-top: 20px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      {% if content %}
        <h1 class="mt-5">Generated Content</h1>
        <div class="image-preview">
          <img src="{{ preview_image_url }}" alt="Uploaded Image">
        </div>
        <h2>Main Content</h2>
        <p>{{ content }}</p>
        <h2>Additional Content</h2>
        <p>{{ additional_content }}</p>
        <a href="{{ url_for('upload_image') }}" class="btn btn-primary">Upload Another Image</a>
      {% else %}
        <h1 class="mt-5">Upload an Image</h1>
        <form method="post" enctype="multipart/form-data">
          <div class="form-group">
            <label for="file">Choose an image file :</label>
            <input type="file" class="form-control-file" id="file" name="file" required>
          </div>
          <button type="submit" class="btn btn-primary">Upload</button>
        </form>
      {% endif %}
    </div>
  </body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
