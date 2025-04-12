from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import redis
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Redis bağlantısı
try:
    redis_client = redis.StrictRedis(
        host='your_redis_host',  # Redis serverin ünvanını burada yazın
        port=6379,  # Portu doğru yazdığınızdan əmin olun
        db=0,
        ssl=False  # SSL varsa True edin, yoxsa False
    )
    print("Redis'e bağlantı sağlandı!")
except Exception as e:
    print(f"Redis bağlantısı hatası: {e}")

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

# Kullanıcı sınıfı
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Kullanıcı yükleyicisi
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Giriş sayfası
@app.route('/')
def home():
    return render_template('index.html')

# Giriş yapmak
@app.route('/login')
def login():
    user = User('1')  # Test amacıyla id'yi sabit koyuyoruz
    login_user(user)
    return redirect(url_for('dashboard'))

# Çıkış yapmak
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Dashboard sayfası
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Hata 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

# Hata 500
@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
