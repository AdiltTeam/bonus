import os
import face_recognition
import cv2
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Quraşdırılacaq olan şəkillər üçün qovluq
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# İcazə verilən fayl növləri
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Fayl uzantısını yoxlamaq üçün funksiya
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Şəkli yükləyin
        if 'image' not in request.files:
            return redirect(request.url)
        image = request.files['image']
        
        if image.filename == '':
            return redirect(request.url)
        
        if image and allowed_file(image.filename):
            # Fayl adı təhlükəsiz bir şəkildə alınır
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            
            # Yüklənmiş şəkili açın və üzləri tanıyın
            image = face_recognition.load_image_file(filepath)
            face_locations = face_recognition.face_locations(image)

            # Əgər üz tapılıbsa, istifadəçiyə göstərmək üçün tanıma nəticəsini göndərin
            if face_locations:
                return render_template('register_form.html', filename=filename)
            else:
                return "Üz tapılmadı, şəkili yenidən çəkib cəhd edin."
    return render_template('register.html')

@app.route('/submit_registration', methods=['POST'])
def submit_registration():
    first_name = request.form['first_name']
    last_name = request.form['last_name']

    # Burada məlumatları verilənlər bazasına və ya başqa bir yerə saxlamaq olar
    return f"Qeydiyyatınız tamamlandı: {first_name} {last_name}"

if __name__ == '__main__':
    app.run(debug=True)
