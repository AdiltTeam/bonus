from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import redis
import os
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Redis Bağlantısı
try:
    redis_client = redis.StrictRedis(
        host='your_redis_host',  # Redis serverin adresini buraya yazın
        port=6379,  # Redis portu
        db=0,
        ssl=False  # Eğer SSL kullanıyorsanız True yapın
    )
    print("Redis'e bağlantı sağlandı!")
except Exception as e:
    print(f"Redis bağlantı hatası: {e}")

# PostgreSQL Bağlantısı
try:
    postgres_conn = psycopg2.connect(
        dbname="adil_33bd", 
        user="adil_33bd_user", 
        password="wCFx6qHuFSRmkQULnnQzIU8oEIbOeSLQ", 
        host="dpg-cvt3lo15pdvs739f3pm0-a", 
        port="5432"
    )
    print("PostgreSQL'e bağlantı sağlandı!")
except Exception as e:
    print(f"PostgreSQL bağlantı hatası: {e}")

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

# Kullanıcı sınıfı
class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        # PostgreSQL üzerinden kullanıcıyı almak
        with postgres_conn.cursor() as cursor:
            query = sql.SQL("SELECT id, username FROM users WHERE id = %s")
            cursor.execute(query, [user_id])
            user = cursor.fetchone()
            if user:
                return User(user[0])
            return None

# Kullanıcı yükleyicisi
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Anasayfa
@app.route('/')
def home():
    return render_template('index.html')

# Giriş yapmak
@app.route('/login')
def login():
    user = User('1')  # Test amacıyla sabit id kullanıyoruz
    login_user(user)
    # Redis'te oturum bilgilerini saklama
    redis_client.set(f"user:{user.id}:logged_in", True)
    return redirect(url_for('dashboard'))

# Çıkış yapmak
@app.route('/logout')
@login_required
def logout():
    redis_client.delete(f"user:{current_user.id}:logged_in")  # Redis'ten oturum bilgisini sil
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
