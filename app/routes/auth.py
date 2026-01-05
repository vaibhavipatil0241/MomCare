from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
from app.data_manager import DataManager
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

class SimpleUser:
    """Simple user class for session management"""
    def __init__(self, user_data):
        self.id = user_data['id']
        self.full_name = user_data['full_name']
        self.email = user_data['email']
        self.role = user_data['role']
        self.is_active = user_data.get('is_active', True)

    def is_authenticated(self):
        return True

    def is_admin(self):
        return self.role == 'admin'

    def is_doctor(self):
        return self.role == 'doctor'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with enhanced security"""
    # Check if user is already logged in
    if session.get('user_id'):
        user_data = DataManager.get_user_by_id(session['user_id'])
        if user_data:
            # Redirect based on user role
            if user_data['role'] == 'admin':
                return redirect('/admin')
            elif user_data['role'] == 'doctor':
                return redirect('/doctor')
            else:
                # Regular users stay on home page
                return redirect('/')

    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
                email = data.get('email', '').strip().lower()
                password = data.get('password', '')
                remember_me = data.get('remember_me', False)
            else:
                email = request.form.get('email', '').strip().lower()
                password = request.form.get('password', '')
                remember_me = request.form.get('remember_me', False)

            # Validate input
            if not email or not password:
                error_msg = 'Please provide both email and password'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('auth/login.html')

            if not validate_email(email):
                error_msg = 'Please provide a valid email address'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('auth/login.html')

            # Authenticate user
            user_data = DataManager.authenticate_user(email, password)

            if user_data:
                if not user_data.get('is_active', True):
                    error_msg = 'Your account has been deactivated. Please contact support.'
                    if request.is_json:
                        return jsonify({'error': error_msg}), 403
                    flash(error_msg, 'error')
                    return render_template('auth/login.html')

                # Login successful
                session['user_id'] = user_data['id']
                session['user_data'] = {
                    'id': user_data['id'],
                    'name': user_data['full_name'],
                    'email': user_data['email'],
                    'role': user_data['role']
                }

                # Redirect based on user role
                if user_data['role'] == 'admin':
                    redirect_url = '/admin'
                elif user_data['role'] == 'doctor':
                    redirect_url = '/doctor'
                else:
                    # Regular users stay on home page
                    redirect_url = '/'

                if request.is_json:
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'user': {
                            'id': user_data['id'],
                            'name': user_data['full_name'],
                            'email': user_data['email'],
                            'role': user_data['role']
                        },
                        'redirect_url': redirect_url
                    })

                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(redirect_url)
            else:
                error_msg = 'Invalid email or password'
                if request.is_json:
                    return jsonify({'error': error_msg}), 401
                flash(error_msg, 'error')

        except Exception as e:
            error_msg = 'An error occurred during login. Please try again.'
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'error')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with enhanced validation"""
    # Check if user is already logged in
    if session.get('user_id'):
        user_data = DataManager.get_user_by_id(session['user_id'])
        if user_data:
            # Redirect based on user role
            if user_data['role'] == 'admin':
                return redirect('/admin')
            elif user_data['role'] == 'doctor':
                return redirect('/doctor')
            else:
                # Regular users stay on home page
                return redirect('/')

    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form

            full_name = data.get('full_name', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            phone = data.get('phone', '').strip()

            # Validate required fields
            if not all([full_name, email, password]):
                error_msg = 'Please fill in all required fields (name, email, password)'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('auth/register.html')

            # Validate email format
            if not validate_email(email):
                error_msg = 'Please provide a valid email address'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('auth/register.html')

            # Validate password
            is_valid, password_msg = validate_password(password)
            if not is_valid:
                if request.is_json:
                    return jsonify({'error': password_msg}), 400
                flash(password_msg, 'error')
                return render_template('auth/register.html')

            # Validate password confirmation
            if confirm_password and password != confirm_password:
                error_msg = 'Passwords do not match'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('auth/register.html')

            # Validate name length
            if len(full_name) < 2:
                error_msg = 'Full name must be at least 2 characters long'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('auth/register.html')

            # Check if user already exists
            if DataManager.get_user_by_email(email):
                error_msg = 'An account with this email address already exists'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('auth/register.html')

            # Create new user
            try:
                user_data = DataManager.create_user({
                    'full_name': full_name,
                    'email': email,
                    'password': password,
                    'role': 'user',
                    'phone': phone
                })

                # Auto-login the user
                session['user_id'] = user_data['id']
                session['user_data'] = {
                    'id': user_data['id'],
                    'name': user_data['full_name'],
                    'email': user_data['email'],
                    'role': user_data['role']
                }
            except Exception as e:
                error_msg = f'Registration failed: {str(e)}'
                if request.is_json:
                    return jsonify({'error': error_msg}), 500
                flash(error_msg, 'error')
                return render_template('auth/register.html')

            redirect_url = '/baby-care'

            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Registration successful! Welcome to Maternal and Child Health Monitoring.',
                    'user': {
                        'id': user_data['id'],
                        'name': user_data['full_name'],
                        'email': user_data['email'],
                        'role': user_data['role']
                    },
                    'redirect_url': redirect_url
                }), 201

            flash('Registration successful! Welcome to Maternal and Child Health Monitoring.', 'success')
            return redirect(redirect_url)

        except Exception as e:
            error_msg = 'Registration failed. Please try again.'
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            flash(error_msg, 'error')

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/check-auth')
@auth_bp.route('/api/check-auth')
def check_auth():
    """Check authentication status"""
    if session.get('user_id'):
        user_data = DataManager.get_user_by_id(session['user_id'])
        if user_data:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user_data['id'],
                    'name': user_data['full_name'],
                    'email': user_data['email'],
                    'role': user_data['role']
                }
            })

    return jsonify({'authenticated': False})

@auth_bp.route('/api/user-data')
def user_data():
    """Get current user data"""
    if session.get('user_id'):
        user_data = DataManager.get_user_by_id(session['user_id'])
        if user_data:
            return jsonify({
                'success': True,
                'user': {
                    'id': user_data['id'],
                    'name': user_data['full_name'],
                    'email': user_data['email'],
                    'role': user_data['role']
                }
            })

    return jsonify({'error': 'Not authenticated'}), 401

