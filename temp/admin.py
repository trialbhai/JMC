from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    complaints = db.relationship('Complaint', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

# Complaint Model
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Notification Model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/dashboard')
@login_required
def dashboard():
    # Sample data for demonstration
    users = [
        {'id': 1, 'username': 'admin', 'role': 'Admin', 'is_active': True},
        {'id': 2, 'username': 'john_doe', 'role': 'User', 'is_active': True},
        {'id': 3, 'username': 'jane_smith', 'role': 'Support', 'is_active': False}
    ]
    
    complaints = [
        {'id': 1, 'title': 'Website Error', 'description': 'Cannot access login page', 'status': 'Open', 'created_at': '2024-03-10'},
        {'id': 2, 'title': 'Payment Issue', 'description': 'Payment not processed', 'status': 'In Progress', 'created_at': '2024-03-09'},
        {'id': 3, 'title': 'Account Access', 'description': 'Reset password not working', 'status': 'Closed', 'created_at': '2024-03-08'}
    ]
    
    current_time = datetime.now()
    notifications = [
        {'id': 1, 'title': 'New User Registration', 'message': 'John Doe has registered', 'is_read': False, 'created_at': (current_time - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M')},
        {'id': 2, 'title': 'System Update', 'message': 'System maintenance scheduled', 'is_read': False, 'created_at': (current_time - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M')},
        {'id': 3, 'title': 'Complaint Resolved', 'message': 'Ticket #123 has been resolved', 'is_read': False, 'created_at': (current_time - timedelta(days=1)).strftime('%Y-%m-%d %H:%M')}
    ]
    
    return render_template('dashboard.html', users=users, complaints=complaints, notifications=notifications)

@app.route('/users')
@login_required
def users():
    # Sample users data
    users = [
        {
            'id': 1,
            'username': 'admin',
            'role': 'Admin'
        },
        {
            'id': 2,
            'username': 'john_doe',
            'role': 'User'
        },
        {
            'id': 3,
            'username': 'jane_smith',
            'role': 'Support'
        }
    ]
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        is_active = request.form.get('is_active') == '1'

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('add_user'))

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            is_active=is_active
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users'))

    return render_template('user_form.html')

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')
        is_active = request.form.get('is_active') == '1'

        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('Username already exists', 'error')
            return redirect(url_for('edit_user', user_id=user_id))

        user.username = username
        user.role = role
        user.is_active = is_active
        db.session.commit()
        return redirect(url_for('users'))

    return render_template('user_form.html', user=user)

@app.route('/users/<int:user_id>/toggle', methods=['POST'])
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True})

@app.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.id == user_id:
        return jsonify({'success': False, 'message': 'Cannot delete yourself'})
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/complaints')
@login_required
def complaints():
    # Sample complaints data
    complaints = [
        {
            'id': 1,
            'title': 'Website Error',
            'description': 'Cannot access login page',
            'status': 'Open',
            'created_at': '2024-03-10',
            'user': 'john_doe'
        },
        {
            'id': 2,
            'title': 'Payment Issue',
            'description': 'Payment not processed',
            'status': 'In Progress',
            'created_at': '2024-03-09',
            'user': 'jane_smith'
        },
        {
            'id': 3,
            'title': 'Account Access',
            'description': 'Reset password not working',
            'status': 'Closed',
            'created_at': '2024-03-08',
            'user': 'mike_wilson'
        },
        {
            'id': 4,
            'title': 'Mobile App Crash',
            'description': 'App crashes on startup',
            'status': 'Open',
            'created_at': '2024-03-07',
            'user': 'sarah_jones'
        },
        {
            'id': 5,
            'title': 'Data Sync Error',
            'description': 'Data not syncing between devices',
            'status': 'In Progress',
            'created_at': '2024-03-06',
            'user': 'john_doe'
        }
    ]
    return render_template('complaints.html', complaints=complaints)

@app.route('/complaints/<int:complaint_id>/messages')
@login_required
def get_complaint_messages(complaint_id):
    messages = Message.query.filter_by(complaint_id=complaint_id).order_by(Message.created_at).all()
    return jsonify([{
        'text': msg.message,
        'isAdmin': msg.is_admin,
        'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M'),
        'user': User.query.get(msg.user_id).username
    } for msg in messages])

@app.route('/complaints/<int:complaint_id>/reply', methods=['POST'])
@login_required
def send_message(complaint_id):
    data = request.get_json()
    message_text = data.get('message')
    status = data.get('status')
    
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Create new message
    message = Message(
        complaint_id=complaint_id,
        user_id=current_user.id,
        message=message_text,
        is_admin=True
    )
    db.session.add(message)
    
    # Update complaint status if changed
    if status and complaint.status != status:
        old_status = complaint.status
        complaint.status = status
        
        # Create notification for status change
        create_notification(
            complaint.user_id,
            'Complaint Status Updated',
            f'Your complaint "{complaint.title}" status has been updated from {old_status} to {status}'
        )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': {
            'text': message_text,
            'isAdmin': True,
            'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M'),
            'user': current_user.username
        }
    })

@app.route('/complaints/<int:complaint_id>', methods=['DELETE'])
@login_required
def delete_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Delete all messages associated with this complaint
    Message.query.filter_by(complaint_id=complaint_id).delete()
    
    # Delete the complaint
    db.session.delete(complaint)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/notifications')
@login_required
def notifications():
    # Sample notifications data with properly formatted dates
    current_time = datetime.now()
    notifications = [
        {
            'id': 1, 
            'title': 'New User Registration', 
            'message': 'John Doe has registered', 
            'is_read': False, 
            'created_at': (current_time - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M')
        },
        {
            'id': 2, 
            'title': 'System Update', 
            'message': 'System maintenance scheduled for tomorrow', 
            'is_read': False, 
            'created_at': (current_time - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M')
        },
        {
            'id': 3, 
            'title': 'Complaint Resolved', 
            'message': 'Ticket #123 has been resolved', 
            'is_read': False, 
            'created_at': (current_time - timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
        },
        {
            'id': 4, 
            'title': 'New Support Ticket', 
            'message': 'New support ticket created by Jane Smith', 
            'is_read': True, 
            'created_at': (current_time - timedelta(days=2)).strftime('%Y-%m-%d %H:%M')
        },
        {
            'id': 5, 
            'title': 'Security Alert', 
            'message': 'Multiple failed login attempts detected', 
            'is_read': True, 
            'created_at': (current_time - timedelta(days=3)).strftime('%Y-%m-%d %H:%M')
        }
    ]
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/notifications/clear', methods=['POST'])
@login_required
def clear_notifications():
    Notification.query.delete()
    db.session.commit()
    return jsonify({'success': True})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def init_db():
    with app.app_context():
        # Drop all tables first
        db.drop_all()
        # Create all tables with new schema
        db.create_all()
        
        try:
            # Create default admin user
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Database initialized successfully with admin user")
        except Exception as e:
            print(f"Error creating admin user: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_db()  # This will now properly recreate the database
    app.run(debug=True, host='127.0.0.1', port=5000) 