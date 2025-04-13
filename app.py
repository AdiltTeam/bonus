from flask import Flask, render_template, request, redirect, url_for
import face_recognition
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Üz tanıma üçün müvəqqəti saxlama yolu
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# İcazə verilən fayl növləri
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Fayl uzantısını yoxlamaq üçün funksiya
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Üz şəkli yüklənir
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Üz tanıma və şəkilin işlənməsi
            image = face_recognition.load_image_file(filepath)
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) > 0:
                # Əgər üz tapıldısa, formu göstər
                return render_template('register_form.html', filename=filename)
            else:
                return "Üz tapılmadı, yenidən cəhd edin."

    return render_template('register_camera.html')

@app.route('/submit_registration', methods=['POST'])
def submit_registration():
    # Ad və soyadın alınması
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    filename = request.form['filename']  # Yüklənmiş şəkil adı

    # Verilənlər bazasına əlavə etmək və ya saxlamaq üçün kodu buraya əlavə edə bilərsiniz.
    return f"Qeydiyyat tamamlandı: {first_name} {last_name}. Yüklənmiş şəkil: {filename}"

if __name__ == '__main__':
    app.run(debug=True)
