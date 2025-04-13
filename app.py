from flask import Flask, render_template, request, redirect, url_for
import face_recognition
import cv2
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Şəkil yüklənir və üz tanıma baş verir
        pass
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
