from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    surname = db.Column(db.String(64), nullable=False)
    customer_code = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    bonus_points = db.Column(db.Integer, default=0)
    profile_picture = db.Column(db.String(255))
    selected_gift_id = db.Column(db.Integer, db.ForeignKey('gift.id', ondelete='SET NULL'), nullable=True)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_notification(self, title, message):
        notification = Notification(title=title, message=message, user=self)
        db.session.add(notification)
        return notification

    @staticmethod
    def create_admin():
        admin = User.query.filter_by(customer_code='ADMIN').first()
        if not admin:
            admin = User()
            admin.name = 'Admin'
            admin.surname = 'User'
            admin.customer_code = 'ADMIN'
            admin.email = 'admin@example.com'
            admin.set_password('admin_melek')
            db.session.add(admin)
            db.session.commit()
            return True
        return False

class Gift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points_required = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, default=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
