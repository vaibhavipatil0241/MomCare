from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from datetime import datetime, date
from werkzeug.security import generate_password_hash
from app.data_manager import DataManager
import json
import sqlite3
import time

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Content update notification system
def trigger_content_update(content_type, action):
    """Trigger content update notification for real-time updates"""
    try:
        # Store update notification in a simple cache/file system
        # In production, this would use Redis, WebSockets, or Server-Sent Events
        update_data = {
            'content_type': content_type,
            'action': action,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat()
        }

        # Store in a simple file-based cache for demo purposes
        # In production, use Redis or a proper message queue
        import os
        cache_dir = os.path.join(current_app.instance_path, 'cache')
        os.makedirs(cache_dir, exist_ok=True)

        cache_file = os.path.join(cache_dir, 'content_updates.json')

        # Read existing updates
        updates = []
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    updates = json.load(f)
            except:
                updates = []

        # Add new update
        updates.append(update_data)

        # Keep only last 100 updates
        updates = updates[-100:]

        # Write back to file
        with open(cache_file, 'w') as f:
            json.dump(updates, f)

        print(f"📡 Content update triggered: {content_type} {action}")

    except Exception as e:
        print(f"Error triggering content update: {e}")
        # Don't fail the main operation if notification fails

def admin_required(f):
    """Decorator to require admin privileges"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        user = DataManager.get_user_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with real-time data"""
    try:
        # Get current user info
        current_user = DataManager.get_user_by_id(session['user_id'])

        # Get basic statistics for initial load
        users = DataManager.get_all_users()
        nutrition_content = DataManager.get_all_nutrition_content()
        # vaccination_schedules = DataManager.get_all_vaccination_schedules()
        faqs = DataManager.get_all_faqs()
        schemes = DataManager.get_all_schemes()
        exercises = DataManager.get_all_exercises()
        meditation_content = DataManager.get_all_meditation_content()
        wellness_tips = DataManager.get_all_wellness_tips()

        # Calculate basic stats
        stats = {
            'users': {
                'total': len(users),
                'admin': len([u for u in users if u.get('role') == 'admin']),
                'doctor': len([u for u in users if u.get('role') == 'doctor']),
                'regular': len([u for u in users if u.get('role') == 'user'])
            },
            'content': {
                'nutrition': len(nutrition_content),
                # 'vaccinations': len(vaccination_schedules),
                'faqs': len(faqs),
                'schemes': len(schemes),
                'exercises': len(exercises),
                'meditation': len(meditation_content),
                'wellness_tips': len(wellness_tips)
            }
        }

        return render_template('admin/dashboard.html',
                             current_user=current_user,
                             initial_stats=stats)
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        return render_template('admin/dashboard.html',
                             current_user={'full_name': 'Administrator'},
                             initial_stats={})

@admin_bp.route('/manage-users')
@admin_required
def manage_users():
    """User management page"""
    return render_template('admin/users.html')

@admin_bp.route('/manage-patients')
@admin_required
def manage_patients():
    """Patient management page"""
    return render_template('admin/manage_patients.html')

@admin_bp.route('/manage-consultations')
@admin_required
def manage_consultations():
    """Consultation management page"""
    return render_template('admin/manage_consultations.html')

@admin_bp.route('/manage-content')
@admin_required
def manage_content():
    """Content management page"""
    return render_template('admin/manage_content.html')

@admin_bp.route('/manage-nutrition')
@admin_required
def manage_nutrition():
    """Nutrition management page"""
    return render_template('admin/manage_nutrition_new.html')

@admin_bp.route('/manage-schemes')
@admin_required
def manage_schemes():
    """Government schemes management page"""
    return render_template('admin/manage_schemes.html')

@admin_bp.route('/manage-faq')
@admin_required
def manage_faq():
    """FAQ management page"""
    return render_template('admin/manage_faq.html')

@admin_bp.route('/manage-exercises')
@admin_required
def manage_exercises():
    """Exercise management page"""
    return render_template('admin/manage_exercises.html')

@admin_bp.route('/manage-meditation')
@admin_required
def manage_meditation():
    """Meditation management page"""
    return render_template('admin/manage_meditation.html')

# API Routes

@admin_bp.route('/api/dashboard-stats')
@admin_required
def dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        # Get statistics using DataManager
        users = DataManager.get_all_users()
        nutrition_content = DataManager.get_all_nutrition_content()
        vaccination_schedules = DataManager.get_all_vaccination_schedules()
        faqs = DataManager.get_all_faqs()
        schemes = DataManager.get_all_schemes()
        exercises = DataManager.get_all_exercises()
        meditation_content = DataManager.get_all_meditation_content()
        wellness_tips = DataManager.get_all_wellness_tips()

        # Calculate user statistics
        total_users = len(users)
        admin_users = len([u for u in users if u.get('role') == 'admin'])
        doctor_users = len([u for u in users if u.get('role') == 'doctor'])
        regular_users = len([u for u in users if u.get('role') == 'user'])

        return jsonify({
            'success': True,
            'stats': {
                'users': {
                    'total': total_users,
                    'admin': admin_users,
                    'doctor': doctor_users,
                    'regular': regular_users
                },
                'content': {
                    'nutrition': len(nutrition_content),
                    'vaccinations': len(vaccination_schedules),
                    'faqs': len(faqs),
                    'schemes': len(schemes),
                    'exercises': len(exercises),
                    'meditation': len(meditation_content),
                    'wellness_tips': len(wellness_tips)
                }
            },
            'recent_activity': {
                'recent_users': users[-5:] if users else [],
                'content_summary': f"{len(nutrition_content)} nutrition, {len(vaccination_schedules)} vaccinations, {len(faqs)} FAQs, {len(schemes)} schemes, {len(exercises)} exercises, {len(meditation_content)} meditations, {len(wellness_tips)} wellness tips"
            },
            'last_updated': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Removed old User model-based API - using DataManager-based API below

# Removed old User model-based API - using DataManager-based API below

# Content Management API Routes

@admin_bp.route('/api/content/nutrition', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def manage_nutrition_content():
    """Manage nutrition content"""
    if request.method == 'GET':
        try:
            # Get nutrition content from DataManager
            nutrition_data = DataManager.get_all_nutrition_content()
            return jsonify({
                'success': True,
                'data': nutrition_data
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()

            # Create new nutrition content
            nutrition_id = DataManager.create_nutrition_content(
                title=data['title'],
                description=data['description'],
                category=data['category'],
                trimester=data['trimester'],
                foods=data.get('foods', []),
                tips=data.get('tips', '')
            )

            # Trigger content update notification
            trigger_content_update('nutrition', 'created')

            return jsonify({
                'success': True,
                'message': 'Nutrition content created successfully',
                'id': nutrition_id
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'PUT':
        try:
            data = request.get_json()
            nutrition_id = data.get('id')

            # Update nutrition content
            DataManager.update_nutrition_content(
                nutrition_id=nutrition_id,
                title=data['title'],
                description=data['description'],
                category=data['category'],
                trimester=data['trimester'],
                foods=data.get('foods', []),
                tips=data.get('tips', '')
            )

            # Trigger content update notification
            trigger_content_update('nutrition', 'updated')

            return jsonify({
                'success': True,
                'message': 'Nutrition content updated successfully'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            nutrition_id = data.get('id')

            # Delete nutrition content
            DataManager.delete_nutrition_content(nutrition_id)

            # Trigger content update notification
            trigger_content_update('nutrition', 'deleted')

            return jsonify({
                'success': True,
                'message': 'Nutrition content deleted successfully'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@admin_bp.route('/api/content/vaccination', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def manage_vaccination_content():
    """Manage vaccination content"""
    if request.method == 'GET':
        try:
            vaccination_data = DataManager.get_all_vaccination_schedules()
            return jsonify({
                'success': True,
                'data': vaccination_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            vaccination_id = DataManager.create_vaccination_schedule(
                vaccine_name=data['vaccine_name'],
                age_months=data['age_months'],
                description=data['description'],
                side_effects=data.get('side_effects', ''),
                precautions=data.get('precautions', '')
            )

            return jsonify({
                'success': True,
                'message': 'Vaccination schedule created successfully',
                'id': vaccination_id
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'PUT':
        try:
            data = request.get_json()
            vaccination_id = data.get('id')

            DataManager.update_vaccination_schedule(
                vaccination_id=vaccination_id,
                vaccine_name=data['vaccine_name'],
                age_months=data['age_months'],
                description=data['description'],
                side_effects=data.get('side_effects', ''),
                precautions=data.get('precautions', '')
            )

            return jsonify({
                'success': True,
                'message': 'Vaccination schedule updated successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            vaccination_id = data.get('id')

            DataManager.delete_vaccination_schedule(vaccination_id)

            return jsonify({
                'success': True,
                'message': 'Vaccination schedule deleted successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@admin_bp.route('/api/content/faq', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def manage_faq_content():
    """Manage FAQ content"""
    if request.method == 'GET':
        try:
            faq_data = DataManager.get_all_faqs()
            return jsonify({
                'success': True,
                'data': faq_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            faq_id = DataManager.create_faq(
                question=data['question'],
                answer=data['answer'],
                category=data['category']
            )

            # Trigger content update notification
            trigger_content_update('faq', 'created')

            return jsonify({
                'success': True,
                'message': 'FAQ created successfully',
                'id': faq_id
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'PUT':
        try:
            data = request.get_json()
            faq_id = data.get('id')

            DataManager.update_faq(
                faq_id=faq_id,
                question=data['question'],
                answer=data['answer'],
                category=data['category']
            )

            # Trigger content update notification
            trigger_content_update('faq', 'updated')

            return jsonify({
                'success': True,
                'message': 'FAQ updated successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            faq_id = data.get('id')

            DataManager.delete_faq(faq_id)

            return jsonify({
                'success': True,
                'message': 'FAQ deleted successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@admin_bp.route('/api/content/schemes', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def manage_schemes_content():
    """Manage government schemes content"""
    if request.method == 'GET':
        try:
            schemes_data = DataManager.get_all_schemes()
            return jsonify({
                'success': True,
                'data': schemes_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            scheme_id = DataManager.create_scheme(
                name=data['name'],
                description=data['description'],
                eligibility=data['eligibility'],
                benefits=data['benefits'],
                how_to_apply=data['how_to_apply'],
                application_link=data.get('application_link'),
                image_url=data.get('image_url')
            )

            return jsonify({
                'success': True,
                'message': 'Government scheme created successfully',
                'id': scheme_id
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'PUT':
        try:
            data = request.get_json()
            scheme_id = data.get('id')

            DataManager.update_scheme(
                scheme_id=scheme_id,
                name=data['name'],
                description=data['description'],
                eligibility=data['eligibility'],
                benefits=data['benefits'],
                how_to_apply=data['how_to_apply'],
                application_link=data.get('application_link'),
                image_url=data.get('image_url')
            )

            return jsonify({
                'success': True,
                'message': 'Government scheme updated successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            scheme_id = data.get('id')

            DataManager.delete_scheme(scheme_id)

            return jsonify({
                'success': True,
                'message': 'Government scheme deleted successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@admin_bp.route('/api/content/exercises', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def manage_exercises_content():
    """Manage exercises content"""
    if request.method == 'GET':
        try:
            exercises_data = DataManager.get_all_exercises()
            return jsonify({
                'success': True,
                'data': exercises_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()

            exercise_id = DataManager.create_exercise(
                name=data['name'],
                category=data['category'],
                trimester=data['trimester'],
                difficulty=data['difficulty'],
                duration=data.get('duration'),
                description=data['description'],
                instructions=data['instructions'],
                precautions=data.get('precautions'),
                benefits=data.get('benefits'),
                equipment=data.get('equipment'),
                video_url=data.get('video_url'),
                image_url=data.get('image_url')
            )

            trigger_content_update('exercises', 'created')

            return jsonify({
                'success': True,
                'message': 'Exercise created successfully',
                'id': exercise_id
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'PUT':
        try:
            data = request.get_json()
            exercise_id = data.get('id')

            DataManager.update_exercise(
                exercise_id=exercise_id,
                name=data['name'],
                category=data['category'],
                trimester=data['trimester'],
                difficulty=data['difficulty'],
                duration=data.get('duration'),
                description=data['description'],
                instructions=data['instructions'],
                precautions=data.get('precautions'),
                benefits=data.get('benefits'),
                equipment=data.get('equipment'),
                video_url=data.get('video_url'),
                image_url=data.get('image_url')
            )

            trigger_content_update('exercises', 'updated')

            return jsonify({
                'success': True,
                'message': 'Exercise updated successfully'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            exercise_id = data.get('id')

            DataManager.delete_exercise(exercise_id)

            trigger_content_update('exercises', 'deleted')

            return jsonify({
                'success': True,
                'message': 'Exercise deleted successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@admin_bp.route('/api/content/meditation', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def manage_meditation_content():
    """Manage meditation content"""
    if request.method == 'GET':
        try:
            meditation_data = DataManager.get_all_meditation_content()
            return jsonify({
                'success': True,
                'data': meditation_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()

            meditation_id = DataManager.create_meditation_content(
                title=data['title'],
                description=data['description'],
                trimester=data['trimester'],
                duration=data['duration'],
                category=data['category'],
                instructions=data['instructions'],
                benefits=data.get('benefits'),
                audio_url=data.get('audio_url'),
                image_url=data.get('image_url'),
                difficulty=data.get('difficulty', 'beginner')
            )

            trigger_content_update('meditation', 'created')

            return jsonify({
                'success': True,
                'message': 'Meditation content created successfully',
                'id': meditation_id
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'PUT':
        try:
            data = request.get_json()
            meditation_id = data.get('id')

            DataManager.update_meditation_content(
                meditation_id=meditation_id,
                title=data['title'],
                description=data['description'],
                trimester=data['trimester'],
                duration=data['duration'],
                category=data['category'],
                instructions=data['instructions'],
                benefits=data.get('benefits'),
                audio_url=data.get('audio_url'),
                image_url=data.get('image_url'),
                difficulty=data.get('difficulty', 'beginner')
            )

            trigger_content_update('meditation', 'updated')

            return jsonify({
                'success': True,
                'message': 'Meditation content updated successfully'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            meditation_id = data.get('id')

            DataManager.delete_meditation_content(meditation_id)

            trigger_content_update('meditation', 'deleted')

            return jsonify({
                'success': True,
                'message': 'Meditation content deleted successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@admin_bp.route('/api/content/wellness-tips', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def manage_wellness_tips():
    """Manage wellness tips"""
    if request.method == 'GET':
        try:
            tips_data = DataManager.get_all_wellness_tips()
            return jsonify({
                'success': True,
                'data': tips_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()

            tip_id = DataManager.create_wellness_tip(
                title=data['title'],
                content=data['content'],
                category=data['category'],
                trimester=data.get('trimester'),
                priority=data.get('priority', 1)
            )

            trigger_content_update('wellness-tips', 'created')

            return jsonify({
                'success': True,
                'message': 'Wellness tip created successfully',
                'id': tip_id
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'PUT':
        try:
            data = request.get_json()
            tip_id = data.get('id')

            DataManager.update_wellness_tip(
                tip_id=tip_id,
                title=data['title'],
                content=data['content'],
                category=data['category'],
                trimester=data.get('trimester'),
                priority=data.get('priority', 1)
            )

            trigger_content_update('wellness-tips', 'updated')

            return jsonify({
                'success': True,
                'message': 'Wellness tip updated successfully'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            tip_id = data.get('id')

            DataManager.delete_wellness_tip(tip_id)

            trigger_content_update('wellness-tips', 'deleted')

            return jsonify({
                'success': True,
                'message': 'Wellness tip deleted successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# User Management API Routes

@admin_bp.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users"""
    try:
        users = DataManager.get_all_users()
        return jsonify({
            'success': True,
            'users': users
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['full_name', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field.replace("_", " ").title()} is required'
                }), 400

        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400

        # Validate role
        valid_roles = ['user', 'doctor', 'admin']
        if data['role'] not in valid_roles:
            return jsonify({
                'success': False,
                'error': 'Invalid role. Must be user, doctor, or admin'
            }), 400

        # Check if email already exists
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM users WHERE email = ?', (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Email already exists'
            }), 400

        # Hash password
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(data['password'])

        # Insert new user
        cursor.execute('''
            INSERT INTO users (full_name, email, password_hash, role, phone, address, date_of_birth, emergency_contact, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['full_name'],
            data['email'],
            password_hash,
            data['role'],
            data.get('phone', ''),
            data.get('address', ''),
            data.get('date_of_birth'),
            data.get('emergency_contact', ''),
            1,  # is_active
            datetime.now().isoformat()
        ))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user_id': user_id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update an existing user"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['full_name', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field.replace("_", " ").title()} is required'
                }), 400

        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400

        # Validate role
        valid_roles = ['user', 'doctor', 'admin']
        if data['role'] not in valid_roles:
            return jsonify({
                'success': False,
                'error': 'Invalid role. Must be user, doctor, or admin'
            }), 400

        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        # Check if email already exists for another user
        cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (data['email'], user_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Email already exists'
            }), 400

        # Prepare update query
        update_fields = []
        update_values = []

        # Always update these fields
        update_fields.extend(['full_name', 'email', 'role', 'phone', 'address', 'date_of_birth', 'emergency_contact'])
        update_values.extend([
            data['full_name'],
            data['email'],
            data['role'],
            data.get('phone', ''),
            data.get('address', ''),
            data.get('date_of_birth'),
            data.get('emergency_contact', '')
        ])

        # Update password if provided
        if data.get('password'):
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(data['password'])
            update_fields.append('password_hash')
            update_values.append(password_hash)

        # Build and execute update query
        set_clause = ', '.join([f'{field} = ?' for field in update_fields])
        update_values.append(user_id)  # Add user_id for WHERE clause

        cursor.execute(f'''
            UPDATE users
            SET {set_clause}
            WHERE id = ?
        ''', update_values)

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'User updated successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_by_id(user_id):
    """Get a specific user by ID"""
    try:
        user = DataManager.get_user_by_id(user_id)
        if user:
            return jsonify({
                'success': True,
                'user': user
            })
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """Update user status"""
    try:
        data = request.get_json()
        is_active = data.get('is_active', True)

        # Update user status in database
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE users
            SET is_active = ?
            WHERE id = ?
        ''', (1 if is_active else 0, user_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'User status updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (soft delete)"""
    try:
        # Soft delete user
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE users
            SET is_active = 0
            WHERE id = ?
        ''', (user_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Patient Management API Routes

@admin_bp.route('/api/patients', methods=['GET'])
@admin_required
def get_patients():
    """Get all patients with detailed information"""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.id, u.full_name, u.email, u.phone, u.role, u.is_active,
                   u.created_at, u.last_login, u.date_of_birth, u.address,
                   u.emergency_contact
            FROM users u
            WHERE u.role IN ('user', 'doctor')
            ORDER BY u.created_at DESC
        ''')

        patients = []
        for row in cursor.fetchall():
            patient = dict(row)
            patients.append(patient)

        conn.close()

        return jsonify({
            'success': True,
            'patients': patients,
            'total_count': len(patients)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/patients', methods=['POST'])
@admin_required
def create_patient():
    """Create a new patient"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['fullName', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400

        # Check if email already exists
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM users WHERE email = ?', (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Email already exists'
            }), 400

        # Hash password
        password_hash = generate_password_hash(data['password'])

        # Insert new patient
        cursor.execute('''
            INSERT INTO users (full_name, email, password_hash, phone, role, is_active,
                             date_of_birth, address, emergency_contact, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (
            data['fullName'],
            data['email'],
            password_hash,
            data.get('phone'),
            data.get('role', 'user'),
            data.get('is_active', True),
            data.get('dateOfBirth'),
            data.get('address'),
            data.get('emergencyContact')
        ))

        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Patient created successfully',
            'patient_id': patient_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Admin Baby / Unique ID management
@admin_bp.route('/api/babies', methods=['GET'])
@admin_required
def admin_get_babies():
    """Return list of babies with unique IDs and parent info for admin management"""
    try:
        babies = DataManager.get_all_unique_ids_for_admin()
        return jsonify({
            'success': True,
            'babies': babies,
            'count': len(babies)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/api/babies/assign', methods=['POST'])
@admin_required
def admin_assign_baby_to_user():
    """Assign a baby (by baby_id or unique_id) to a user (parent) and optionally update unique_id

    Payload:
    {
        "baby_id": 123,           # optional if unique_id provided
        "unique_id": "BABY-2024-...",  # optional if baby_id provided
        "user_id": 456,           # target parent user id
        "new_unique_id": "..."  # optional - to change unique id
    }
    """
    try:
        data = request.get_json() or {}
        baby_id = data.get('baby_id')
        unique_id = data.get('unique_id')
        user_id = data.get('user_id')
        new_unique_id = data.get('new_unique_id')

        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400

        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()

        # find baby by id or unique_id
        if baby_id:
            cursor.execute('SELECT id, parent_id, unique_id FROM babies WHERE id = ? AND is_active = 1', (baby_id,))
        else:
            cursor.execute('SELECT id, parent_id, unique_id FROM babies WHERE unique_id = ? AND is_active = 1', (unique_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Baby not found'}), 404

        found_baby_id, old_parent_id, old_unique_id = row[0], row[1], row[2]

        # verify target user exists
        cursor.execute('SELECT id, full_name, email FROM users WHERE id = ? AND is_active = 1', (user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            conn.close()
            return jsonify({'success': False, 'error': 'Target user not found'}), 404

        # Update parent_id
        cursor.execute('UPDATE babies SET parent_id = ? WHERE id = ?', (user_id, found_baby_id))

        # Update unique id if requested
        unique_changed = False
        if new_unique_id:
            # ensure uniqueness
            cursor.execute('SELECT id FROM babies WHERE unique_id = ? AND id != ?', (new_unique_id, found_baby_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'error': 'Requested new_unique_id already in use'}), 400

            cursor.execute('UPDATE babies SET unique_id = ? WHERE id = ?', (new_unique_id, found_baby_id))
            unique_changed = True

        conn.commit()

        # Log unique id change when appropriate
        if unique_changed:
            DataManager.log_unique_id_change(found_baby_id, old_unique_id, new_unique_id, reason='Admin reassignment')

        conn.close()

        return jsonify({
            'success': True,
            'message': 'Baby assignment updated successfully',
            'baby_id': found_baby_id,
            'old_parent_id': old_parent_id,
            'new_parent_id': user_id,
            'old_unique_id': old_unique_id,
            'new_unique_id': new_unique_id if unique_changed else old_unique_id
        })

    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/patients/<int:patient_id>', methods=['PUT'])
@admin_required
def update_patient(patient_id):
    """Update an existing patient"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['fullName', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400

        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()

        # Check if patient exists
        cursor.execute('SELECT id FROM users WHERE id = ?', (patient_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404

        # Check if email already exists for another user
        cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (data['email'], patient_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Email already exists'
            }), 400

        # Update patient
        cursor.execute('''
            UPDATE users
            SET full_name = ?, email = ?, phone = ?, role = ?, is_active = ?,
                date_of_birth = ?, address = ?, emergency_contact = ?
            WHERE id = ?
        ''', (
            data['fullName'],
            data['email'],
            data.get('phone'),
            data.get('role', 'user'),
            data.get('is_active', True),
            data.get('dateOfBirth'),
            data.get('address'),
            data.get('emergencyContact'),
            patient_id
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Patient updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/patients/<int:patient_id>', methods=['GET'])
@admin_required
def get_patient_by_id(patient_id):
    """Get a specific patient by ID"""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.id, u.full_name, u.email, u.phone, u.role, u.is_active,
                   u.created_at, u.last_login, u.date_of_birth, u.address,
                   u.emergency_contact
            FROM users u
            WHERE u.id = ? AND u.role IN ('user', 'doctor')
        ''', (patient_id,))

        patient = cursor.fetchone()
        conn.close()

        if patient:
            return jsonify({
                'success': True,
                'patient': dict(patient)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/patients/<int:patient_id>/status', methods=['PUT'])
@admin_required
def update_patient_status(patient_id):
    """Update patient status"""
    try:
        data = request.get_json()
        is_active = data.get('is_active', True)

        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()

        # Check if patient exists
        cursor.execute('SELECT id FROM users WHERE id = ? AND role IN ("user", "doctor")', (patient_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404

        # Update status
        cursor.execute('UPDATE users SET is_active = ? WHERE id = ?', (is_active, patient_id))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Patient {"activated" if is_active else "deactivated"} successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/patients/<int:patient_id>', methods=['DELETE'])
@admin_required
def delete_patient(patient_id):
    """Delete patient (soft delete)"""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()

        # Check if patient exists
        cursor.execute('SELECT id FROM users WHERE id = ? AND role IN ("user", "doctor")', (patient_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404

        # Soft delete patient (set is_active to 0)
        cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (patient_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Patient deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/patients/statistics', methods=['GET'])
@admin_required
def get_patient_statistics():
    """Get patient statistics for dashboard"""
    try:
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()

        # Get total patients
        cursor.execute('SELECT COUNT(*) FROM users WHERE role IN ("user", "doctor")')
        total_patients = cursor.fetchone()[0]

        # Get active patients
        cursor.execute('SELECT COUNT(*) FROM users WHERE role IN ("user", "doctor") AND is_active = 1')
        active_patients = cursor.fetchone()[0]

        # Get new patients this month
        cursor.execute('''
            SELECT COUNT(*) FROM users
            WHERE role IN ("user", "doctor")
            AND date(created_at) >= date('now', 'start of month')
        ''')
        new_patients_this_month = cursor.fetchone()[0]

        # Get patients by role
        cursor.execute('''
            SELECT role, COUNT(*) as count
            FROM users
            WHERE role IN ("user", "doctor")
            GROUP BY role
        ''')
        patients_by_role = dict(cursor.fetchall())

        conn.close()

        return jsonify({
            'success': True,
            'statistics': {
                'total_patients': total_patients,
                'active_patients': active_patients,
                'inactive_patients': total_patients - active_patients,
                'new_patients_this_month': new_patients_this_month,
                'patients_by_role': patients_by_role
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



