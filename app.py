from flask import Flask, render_template
import logging
from logging import FileHandler
from sqlalchemy import text

app = Flask(__name__)

# Log faylına məlumat yazmaq
if not app.debug:
    file_handler = FileHandler('app_errors.log')
    file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(file_handler)

@app.route('/')
def home():
    try:
        result = db.session.execute(text("SELECT * FROM users LIMIT 5")).fetchall()
        return str(result)  # Əgər səhv yoxdur, nəticəni qaytarırıq
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

# 500 səhvini idarə etmək üçün handler
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal Server Error: {str(error)}")  # Xətanın loglanması
    return render_template('errors/500.html', error=str(error)), 500

if __name__ == '__main__':
    app.run(debug=True)
