from flask import Flask, request, render_template_string
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ''
    message = ''
    uploaded_files = os.listdir(UPLOAD_FOLDER)

    if request.method == 'POST':
        # Handle file upload
        if 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
                uploaded_file.save(filepath)
                message = f"File '{uploaded_file.filename}' uploaded."

        elif 'filename_to_check' in request.form:
            filename_to_check = request.form.get('filename_to_check', '')
            try:
                # Prevent path traversal by sanitizing input (removing dangerous characters)
                safe_filename = os.path.basename(filename_to_check)
                unsafe_path = os.path.join(UPLOAD_FOLDER, safe_filename)

                # Running the file command directly using subprocess (Windows command)
                command = f'echo {unsafe_path}' 
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    result = result.stdout  # Command output
                else:
                    result = f"Error: {result.stderr}"

            except Exception as e:
                result = f'Error: {e}'

    # Refresh file list
    uploaded_files = os.listdir(UPLOAD_FOLDER)

    return render_template_string('''
        <!doctype html>
        <title>File Upload and Check</title>
        <h1>Upload a File</h1>
        <form method=post enctype=multipart/form-data>
            <input type=file name=file>
            <input type=submit value=Upload>
        </form>
        <p>{{ message }}</p>

        <h2>Uploaded Files:</h2>
        <ul>
        {% for f in uploaded_files %}
            <li>{{ f }}</li>
        {% endfor %}
        </ul>

        <h2>Check a File</h2>
        <form method=post>
            <input type=text name=filename_to_check placeholder="Enter filename">
            <input type=submit value=Check>
        </form>
        <pre>{{ result }}</pre>
    ''', uploaded_files=uploaded_files, result=result, message=message)

if __name__ == '__main__':
    app.run(debug=True)
