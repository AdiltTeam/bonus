from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import FileHandler

# Tətbiqi və DB-ni başlatmaq
app = Flask(__name__)

# PostgreSQL verilənlər bazası konfiqurasiyası (daha əvvəl verdiyiniz URL ilə)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://adil_33bd_user:wCFx6qHuFSRmkQULnnQzIU8oEIbOeSLQ@dpg-cvt3lo15pdvs739f3pm0-a/adil_33bd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db obyektini yaratmaq
db = SQLAlchemy(app)

# Log faylına məlumat yazmaq
if not app.debug:
    file_handler = FileHandler('app_errors.log')
    file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(file_handler)

# Anasəhifə route'u
@app.route('/')
def home():
    try:
        # Verilənlər bazasına sorğu göndərmək
        result = db.session.execute("SELECT * FROM users LIMIT 5").fetchall()
        return str(result)  # Nəticəni göstəririk
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

# 'pano' adlı dashboard səhifəsini göstərən route
@app.route('/pano')
def pano():
    return render_template('dashboard.html')  # dashboard.html şablonunu əlavə edin

# 500 səhvini idarə etmək üçün handler
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal Server Error: {str(error)}")  # Xətanın loglanması
    return render_template('errors/500.html', error=str(error)), 500

if __name__ == '__main__':
    app.run(debug=True)
