from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Uygulama ve veritabanı yapılandırması
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Güvenlik için bir anahtar
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://adil_33bd_user:wCFx6qHuFSRmkQULnnQzIU8oEIbOeSLQ@dpg-cvt3lo15pdvs739f3pm0-a/adil_33bd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login yapılandırması
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Giriş yapılmamışsa yönlendirecek sayfa

# Kullanıcı modelini tanımlıyoruz
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Flask-Login'in kullanıcı yükleme fonksiyonu
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ana sayfa
@app.route('/')
def home():
    return render_template('home.html')

# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Burada password doğrulaması basit tutuldu, daha güvenli bir yöntem kullanın!
            login_user(user)
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Kullanıcı adı veya şifre yanlış!', 'danger')
    
    return render_template('login.html')

# Dashboard sayfası, giriş yapmış kullanıcılar için
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Çıkış yapma fonksiyonu
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Çıkış yapıldı!', 'info')
    return redirect(url_for('home'))

# Kullanıcı kayıt sayfası (opsiyonel)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten alınmış!', 'warning')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Hesap başarıyla oluşturuldu!', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

# Veritabanını oluşturma (İlk defa çalıştırıldığında kullanılır)
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
