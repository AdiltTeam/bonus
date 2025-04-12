from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from sqlalchemy import text  # text metodunu əlavə edin
import os

# Flask tətbiqini yaratmaq
app = Flask(__name__)

# PostgreSQL əlaqəsini qurmaq
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://adil_33bd_user:wCFx6qHuFSRmkQULnnQzIU8oEIbOeSLQ@dpg-cvt3lo15pdvs739f3pm0-a/adil_33bd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy obyektini yaratmaq
db = SQLAlchemy(app)

# Redis bağlantısı üçün doğru URL
app.config['REDIS_URL'] = 'redis://:AUauAAIjcDFlMzllYmIxYzY5MWQ0NTVmYTU4NGQ4MTY1ODc5MDUxN3AxMA@dear-dory-18094.upstash.io:6379'
redis = Redis.from_url(app.config['REDIS_URL'])

# Anasəhifə üçün route
@app.route('/')
def home():
    # SQLAlchemy ilə doğru SQL sorğusunu yazın
    result = db.session.execute(text("SELECT * FROM users LIMIT 5")).fetchall()  # text() ilə düzəldildi

    # Redis ilə əlaqəli məlumatı alırıq (məsələn, sayğac dəyəri)
    counter = redis.get('counter')
    if counter is None:
        counter = 0
    else:
        counter = int(counter)

    return render_template('index.html', result=result, counter=counter)

# Xətalar üçün səhifə
@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

# Tətbiqi başlatmaq
if __name__ == '__main__':
    app.run(debug=True)
