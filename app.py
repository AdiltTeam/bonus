from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://adil_33bd_user:wCFx6qHuFSRmkQULnnQzIU8oEIbOeSLQ@dpg-cvt3lo15pdvs739f3pm0-a/adil_33bd'
db = SQLAlchemy(app)

@app.route('/')
def home():
    try:
        result = db.session.execute(text("SELECT * FROM users LIMIT 5")).fetchall()
        return render_template('index.html', users=result)
    except Exception as e:
        return render_template('errors/500.html', error=str(e))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
