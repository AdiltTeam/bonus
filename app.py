from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
import face_recognition
import cv2
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
Bootstrap(app)

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# Register page route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Capture the face encoding logic here
        image_file = request.files['image']
        image = face_recognition.load_image_file(image_file)
        encoding = face_recognition.face_encodings(image)
        
        if encoding:
            flash("Face registered successfully!", 'success')
        else:
            flash("No face found in the image!", 'danger')
        return redirect(url_for('register'))
    
    return render_template('register_form.html')

# Camera registration route
@app.route('/register_camera', methods=['GET', 'POST'])
def register_camera():
    return render_template('register_camera.html')

if __name__ == '__main__':
    app.run(debug=True)
