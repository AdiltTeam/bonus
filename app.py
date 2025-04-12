import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, send_from_directory
import redis
from redis.exceptions import ConnectionError as RedisConnectionError
from extensions import init_extensions, db, sse
import time

# Create the app
app = Flask(__name__)

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/customer_bonus.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Customer Bonus startup')

# Configure the app
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "a secret key")
app.config['STATIC_FOLDER'] = 'static'

# Set production configuration
app.config['DEBUG'] = False
app.config['ENV'] = 'production'

# Redis connection configuration
REDIS_RETRY_ATTEMPTS = 3
REDIS_RETRY_DELAY = 2  # seconds
REDIS_CONFIG = {
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'socket_keepalive': True,
    'health_check_interval': 30,
    'retry_on_timeout': True,
    'decode_responses': True
}

# Configure Redis for real-time notifications (disabled by default)
app.config['NOTIFICATIONS_ENABLED'] = False

# Redis URL - Localhost istifadə edirik
redis_url = "redis://localhost:6379"

app.config["REDIS_URL"] = redis_url
app.config["SSE_REDIS_URL"] = redis_url

def connect_redis_with_retry():
    """Attempt to connect to Redis with retry logic"""
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
                app.logger.warning(f"Redis connection attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                app.logger.error(f"Failed to connect to Redis after {REDIS_RETRY_ATTEMPTS} attempts")
                return None
        except Exception as e:
            app.logger.error(f"Unexpected Redis error: {str(e)}")
            return None

# Try to initialize Redis connection
redis_client = connect_redis_with_retry()
if redis_client:
    app.config['NOTIFICATIONS_ENABLED'] = True
    app.config['REDIS_PUBSUB_OPTIONS'] = {
        'channel_prefix': 'sse',
        'retry_interval': 5000,
        'max_retry_interval': 30000
    }
else:
    app.logger.warning("Redis connection failed, falling back to database-only notifications")

# Configure SQLAlchemy database URL - Localhost istifadə edirik
try:
    mysql_host = "localhost"
    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_password = os.environ.get('MYSQL_PASSWORD', '')
    mysql_database = os.environ.get('MYSQL_DATABASE', 'test')
    mysql_port = os.environ.get('MYSQL_PORT', '3306')

    if not all([mysql_user, mysql_password, mysql_database]):
        raise ValueError("Missing required database configuration")

    app.logger.info(f"Configuring database connection to {mysql_host}:{mysql_port}/{mysql_database}")

    from urllib.parse import quote_plus
    password = quote_plus(mysql_password)
    username = quote_plus(mysql_user)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{username}:{password}@{mysql_host}:{mysql_port}/{mysql_database}?ssl=false"
    )

    # Configure SQLAlchemy connection pool
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_timeout": 30,
        "pool_size": 10,
        "max_overflow": 5
    }

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

except Exception as e:
    app.logger.error(f"Database configuration error: {str(e)}")
    raise

# Configure static file handling for production
@app.route('/static/<path:filename>')
def serve_static(filename):
    cache_timeout = 2592000  # 30 days
    return send_from_directory(
        app.static_folder or 'static',
        filename,
        cache_timeout=cache_timeout
    )

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page not found: {error}')
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Server Error: {error}')
    return render_template('errors/500.html'), 500

# Initialize extensions
try:
    init_extensions(app)
    app.logger.info("Extensions initialized successfully")
except Exception as e:
    app.logger.error(f"Failed to initialize extensions: {str(e)}")
    raise

# Import routes after app is created
import routes  # noqa: F401
import admin  # noqa: F401
