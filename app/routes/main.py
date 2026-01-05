from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from app.data_manager import DataManager
from datetime import datetime
import sqlite3

main_bp = Blueprint('main', __name__)

def login_required(f):
    """Simple login required decorator"""
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@main_bp.route('/')
def index():
    """Main landing page - show home page with user context if logged in"""
    user_data = None
    if session.get('user_id'):
        try:
            user_data = DataManager.get_user_by_id(session['user_id'])
        except:
            pass
    return render_template('home.html', user=user_data)

@main_bp.route('/home')
def home():
    """Home page - show home page with user context if logged in"""
    user_data = None
    if session.get('user_id'):
        try:
            user_data = DataManager.get_user_by_id(session['user_id'])
        except:
            pass
    return render_template('home.html', user=user_data)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Unified dashboard - shows content based on user role without automatic redirect"""
    try:
        user_data = DataManager.get_user_by_id(session['user_id'])
        if user_data:
            # Pass user data to template so it can show appropriate content/navigation
            return render_template('dashboard.html', user=user_data)
        else:
            # If no user data, redirect to login
            return redirect('/auth/login')
    except Exception as e:
        # If there's any error, redirect to login
        print(f"Dashboard error: {e}")
        return redirect('/auth/login')

@main_bp.route('/pregnancy-care')
@login_required
def pregnancy_care():
    """Pregnancy care main page"""
    return redirect('/pregnancy')

@main_bp.route('/baby-care')
@login_required
def baby_care():
    """Baby care main page"""
    return redirect('/babycare')

@main_bp.route('/nutrition')
def nutrition():
    """Nutrition guide page"""
    return render_template('pregnancy/nutrition.html')

@main_bp.route('/vaccination')
def vaccination():
    """Vaccination schedule page"""
    return render_template('vaccination/vaccination.html')

@main_bp.route('/faq')
def faq():
    """FAQ page"""
    return render_template('faq/faq.html')

@main_bp.route('/government-schemes')
def government_schemes():
    """Government schemes page"""
    return render_template('schemes/schemes.html')

@main_bp.route('/exercises')
def exercises():
    """Exercise guide page"""
    return render_template('exercises/exercises.html')

@main_bp.route('/meditation')
def meditation():
    """Meditation guide page"""
    return render_template('meditation/meditation.html')

@main_bp.route('/my-appointments')
@login_required
def my_appointments():
    """Doctor's appointments page - only accessible by doctors"""
    try:
        user_data = DataManager.get_user_by_id(session['user_id'])

        # Check if user is a doctor
        if user_data.role != 'doctor':
            flash('Access denied. Only doctors can view this page.', 'error')
            return redirect('/dashboard')

        # Redirect to doctor appointments page
        return redirect('/doctor/appointments')
    except Exception as e:
        print(f"My appointments error: {e}")
        return redirect('/auth/login')

@main_bp.route('/test-appointments-api')
def test_appointments_api():
    """Test route for appointments API"""
    return jsonify({
        'success': True,
        'message': 'Appointments API test route is working!',
        'timestamp': datetime.now().isoformat()
    })

@main_bp.route('/my-reports')
@login_required
def my_reports():
    """User's medical reports page"""
    try:
        user_data = DataManager.get_user_by_id(session['user_id'])

        # Only allow regular users (patients) to access this page
        if user_data.get('role') == 'doctor':
            return redirect('/doctor/reports')
        elif user_data.get('role') == 'admin':
            return redirect('/admin')

        return render_template('user_reports.html', user=user_data)
    except Exception as e:
        print(f"My reports error: {e}")
        return redirect('/auth/login')

@main_bp.route('/test-api')
def test_api():
    """Serve the API test page"""
    from flask import send_from_directory
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return send_from_directory(base_dir, 'test_api.html')

@main_bp.route('/api/my-reports')
@login_required
def get_my_reports():
    """Get medical reports for the current user (patient)"""
    try:
        user_id = session['user_id']

        conn = DataManager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT r.id, r.patient_id, r.doctor_id, r.patient_name, r.doctor_name,
                   r.report_type, r.report_date, r.findings, r.recommendations,
                   r.diagnosis, r.notes, r.created_at, r.updated_at
            FROM medical_reports r
            WHERE r.patient_id = ? AND r.is_active = 1
            ORDER BY r.report_date DESC, r.created_at DESC
        ''', (user_id,))

        reports = cursor.fetchall()
        conn.close()

        # Convert to list of dictionaries
        reports_list = []
        for report in reports:
            reports_list.append({
                'id': report['id'],
                'patientId': report['patient_id'],
                'doctorId': report['doctor_id'],
                'patientName': report['patient_name'],
                'doctorName': report['doctor_name'],
                'reportType': report['report_type'],
                'date': report['report_date'],
                'findings': report['findings'],
                'recommendations': report['recommendations'] or '',
                'diagnosis': report['diagnosis'] or '',
                'notes': report['notes'] or '',
                'createdAt': report['created_at'],
                'updatedAt': report['updated_at']
            })

        return jsonify({
            'success': True,
            'reports': reports_list
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"GET MY REPORTS ERROR: {str(e)}")
        print(f"FULL TRACEBACK: {error_details}")

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
