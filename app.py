import os
import logging
import psycopg2
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from redis.exceptions import ConnectionError as RedisConnectionError
import redis
import time
from dotenv import load_dotenv

load_dotenv()

# Flask app
app = Flask(__name__)

# Logging setup
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/customer_bonus.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Customer Bonus startup')

# Configuration
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "qX8wX9JphFlGdrbCvqJVaZ4Z9dKPtxM5qpRPRGdz4TY")
app.config['STATIC_FOLDER'] = 'static'
app.config['DEBUG'] = False
app.config['ENV'] = 'production'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://adil_33bd_user:wCFx6qHuFSRmkQULnnQzIU8oEIbOeSLQ@dpg-cvt3lo15pdvs739f3pm0-a.oregon-postgres.render.com/adil_33bd'
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
    "pool_timeout": 30,
    "pool_size": 10,
    "max_overflow": 5
}

# Database
db = SQLAlchemy(app)

# Login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Redis connection (optional)
REDIS_RETRY_ATTEMPTS = 3
REDIS_RETRY_DELAY = 2
REDIS_CONFIG = {
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'socket_keepalive': True,
    'health_check_interval': 30,
    'retry_on_timeout': True,
    'decode_responses': True
}

# Redis URL with endpoint, port, password and SSL
redis_url = os.environ.get("REDIS_URL", "redis://AUauAAIjcDFlMzllYmIxYzY5MWQ0NTVmYTU4NGQ4MTY1ODc5MDUxN3AxMA:6379@dear-dory-18094.upstash.io:6379?ssl=True")

def connect_redis_with_retry():
    app.logger.info("Attempting to connect to Redis")
    for attempt in range(REDIS_RETRY_ATTEMPTS):
        try:
            redis_client = redis.from_url(redis_url, **REDIS_CONFIG)
            redis_client.ping()
            app.logger.info("Redis connection successful")
            return redis_client
        except RedisConnectionError as e:
            if attempt < REDIS_RETRY_ATTEMPTS - 1:
                wait_time = REDIS_RETRY_DELAY * (attempt + 1)
                app.logger.warning(f"Redis attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                app.logger.error("Failed to connect to Redis after retries")
                return None
        except Exception as e:
            app.logger.error(f"Unexpected Redis error: {str(e)}")
            return None

redis_client = connect_redis_with_retry() if redis_url else None
if redis_client:
    app.config['NOTIFICATIONS_ENABLED'] = True
    app.config['REDIS_PUBSUB_OPTIONS'] = {
        'channel_prefix': 'sse',
        'retry_interval': 5000,
        'max_retry_interval': 30000
    }
else:
    app.logger.warning("Redis connection failed, using DB-only notifications")

# Error pages
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page not found: {error}')
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Server Error: {error}')
    return render_template('errors/500.html'), 500

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename, cache_timeout=2592000)

# Import routes
import routes  # noqa: F401
import admin   # noqa: F401

# Run app
if __name__ == '__main__':
    app.run()
