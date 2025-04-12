from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import app
from extensions import db
from models import User, Gift, Notification
from forms import LoginForm, RegistrationForm, SettingsForm
from utils import save_picture
from datetime import datetime
from sqlalchemy import or_

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.customer_code == 'ADMIN':
            return redirect('/admin/')
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            or_(
                User.customer_code == form.identifier.data,
                User.email == form.identifier.data
            )
        ).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid identifier or password')
            return redirect(url_for('login'))
            
        login_user(user)
        
        # Redirect admin users to admin panel
        if user.customer_code == 'ADMIN':
            return redirect('/admin/')
        return redirect(url_for('dashboard'))
        
    return render_template('login.html', title='Sign In', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.customer_code == 'ADMIN':
        return redirect('/admin/')
        
    notifications = current_user.notifications.filter_by(read=False).order_by(Notification.timestamp.desc()).limit(5).all()
    selected_gift = Gift.query.get(current_user.selected_gift_id) if current_user.selected_gift_id else None
    return render_template('dashboard.html', notifications=notifications, selected_gift=selected_gift)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            customer_code=form.customer_code.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
        
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.email = form.email.data
        
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data)
            current_user.profile_picture = picture_file
            
        db.session.commit()
        flash('Your settings have been updated!')
        return redirect(url_for('settings'))
        
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        
    return render_template('settings.html', title='Settings', form=form)

@app.route('/gift_selection')
@login_required
def gift_selection():
    gifts = Gift.query.filter_by(available=True).all()
    return render_template('gift_selection.html', gifts=gifts)

@app.route('/select_gift/<int:gift_id>')
@login_required
def select_gift(gift_id):
    gift = Gift.query.get_or_404(gift_id)
    if not gift.available:
        flash('This gift is no longer available.')
        return redirect(url_for('gift_selection'))
        
    current_user.selected_gift_id = gift_id
    db.session.commit()
    flash(f'You have selected {gift.name} as your gift!')
    return redirect(url_for('dashboard'))

@app.route('/redeem_gift')
@login_required
def redeem_gift():
    if not current_user.selected_gift_id:
        flash('Please select a gift first.')
        return redirect(url_for('gift_selection'))
        
    gift = Gift.query.get(current_user.selected_gift_id)
    if not gift:
        flash('Selected gift not found.')
        return redirect(url_for('gift_selection'))
        
    if not gift.available:
        flash('This gift is no longer available.')
        current_user.selected_gift_id = None
        db.session.commit()
        return redirect(url_for('gift_selection'))
        
    if current_user.bonus_points < gift.points_required:
        flash('You do not have enough points to redeem this gift.')
        return redirect(url_for('dashboard'))
        
    current_user.bonus_points -= gift.points_required
    current_user.selected_gift_id = None
    db.session.commit()
    
    flash(f'Congratulations! You have successfully redeemed {gift.name}!')
    return redirect(url_for('dashboard'))

@app.route('/notifications/poll')
@login_required
def poll_notifications():
    notifications = current_user.notifications.filter_by(read=False).order_by(Notification.timestamp.desc()).all()
    return jsonify({
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'timestamp': n.timestamp.isoformat()
        } for n in notifications]
    })

@app.route('/notifications/mark_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    notification.read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.customer_code == 'ADMIN':
        return redirect('/admin/')
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(customer_code='ADMIN').first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect('/admin/')
        flash('Invalid admin credentials')
        
    return render_template('admin_login.html', title='Admin Login', form=form)