from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from app.data_manager import DataManager
import json
from datetime import datetime, date

demo_bp = Blueprint('demo', __name__)

def login_required(f):
    """Simple login required decorator"""
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    """Admin required decorator"""
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))

        user_data = DataManager.get_user_by_id(session['user_id'])
        if not user_data or user_data['role'] != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@demo_bp.route('/baby-care')
@login_required
def baby_care():
    """Baby care main page"""
    return render_template('babycare/babycare.html')

@demo_bp.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')

@demo_bp.route('/admin/manage-vaccination')
@admin_required
def admin_vaccination():
    """Admin vaccination management"""
    return render_template('admin/manage_vaccination.html')

# API endpoints with real data

@demo_bp.route('/api/admin/baby-care-stats')
@admin_required
def demo_baby_care_stats():
    """Baby care statistics"""
    try:
        stats = DataManager.get_statistics()
        return jsonify({
            'success': True,
            'stats': {
                'total_users': stats['total_users'],
                'active_sessions': 1,  # Simplified for demo
                'baby_records': stats['total_babies'],
                'total_babies': stats['total_babies'],
                'total_vaccinations': stats['total_vaccinations'],
                'total_nutrition_records': stats['total_nutrition_records'],

                'total_growth_records': stats['total_growth_records']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@demo_bp.route('/admin/api/dashboard-stats')
@admin_required
def demo_dashboard_stats():
    """Dashboard statistics with real data"""
    try:
        users = DataManager.get_all_users()
        babies = DataManager.get_all_babies()
        vaccinations = DataManager.get_all_vaccinations()

        # Calculate user statistics
        user_stats = {
            'total': len(users),
            'admin': len([u for u in users if u['role'] == 'admin']),
            'doctor': len([u for u in users if u['role'] == 'doctor']),
            'regular': len([u for u in users if u['role'] == 'user'])
        }

        # Calculate vaccination statistics
        completed_vaccinations = len([v for v in vaccinations if v['status'] == 'completed'])
        pending_vaccinations = len([v for v in vaccinations if v['status'] == 'scheduled'])

        # Get recent activity
        recent_users = sorted(users, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        recent_babies = sorted(babies, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        recent_appointments = DataManager.get_recent_appointments(limit=5)
        recent_unique_ids = DataManager.get_recent_unique_ids(limit=5)

        return jsonify({
            'success': True,
            'stats': {
                'users': user_stats,
                'baby_care': {
                    'total_babies': len(babies),
                    'total_vaccinations': len(vaccinations),
                    'pending_vaccinations': pending_vaccinations,
                    'completed_vaccinations': completed_vaccinations
                },
                'pregnancy': {
                    'total_pregnancies': 0  # Not implemented yet
                },
                'appointments': {
                    'total': 0,  # Not implemented yet
                    'pending': 0
                }
            },
            'recent_activity': {
                'recent_users': recent_users,
                'recent_babies': recent_babies,
                'recent_appointments': recent_appointments,
                'recent_unique_ids': recent_unique_ids
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@demo_bp.route('/admin/api/vaccination-schedule')
def demo_vaccination_schedule():
    """Demo vaccination schedule"""
    return jsonify({
        'success': True,
        'vaccinations': [
            {
                'id': 1,
                'vaccine_name': 'BCG',
                'baby_name': 'Baby Emma',
                'scheduled_date': '2024-09-15',
                'administered_date': None,
                'status': 'scheduled',
                'doctor_name': 'Dr. Smith',
                'is_overdue': False
            },
            {
                'id': 2,
                'vaccine_name': 'Hepatitis B',
                'baby_name': 'Baby Liam',
                'scheduled_date': '2024-08-25',
                'administered_date': '2024-08-25',
                'status': 'completed',
                'doctor_name': 'Dr. Johnson',
                'is_overdue': False
            },
            {
                'id': 3,
                'vaccine_name': 'DPT',
                'baby_name': 'Baby Sophia',
                'scheduled_date': '2024-08-30',
                'administered_date': None,
                'status': 'scheduled',
                'doctor_name': 'Dr. Brown',
                'is_overdue': True
            }
        ],
        'upcoming_count': 1,
        'overdue_count': 1
    })

@demo_bp.route('/babycare/api/admin/all-babies')
@admin_required
def demo_all_babies():
    """All babies list with real data"""
    try:
        babies = DataManager.get_all_babies()
        users = DataManager.get_all_users()

        # Create a user lookup dictionary
        user_lookup = {user['id']: user for user in users}

        babies_with_parents = []
        for baby in babies:
            parent = user_lookup.get(baby['parent_id'])
            baby_data = baby.copy()
            baby_data['parent_name'] = parent['full_name'] if parent else 'Unknown'
            baby_data['parent_email'] = parent['email'] if parent else 'Unknown'
            babies_with_parents.append(baby_data)

        return jsonify({
            'success': True,
            'babies': babies_with_parents
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@demo_bp.route('/api/babies', methods=['GET', 'POST'])
@login_required
def babies_api():
    """Get babies for current user or create a new baby"""
    if request.method == 'GET':
        try:
            user_data = DataManager.get_user_by_id(session['user_id'])
            is_admin = user_data['role'] == 'admin'
            babies = DataManager.get_babies_for_user(session['user_id'], is_admin)

            return jsonify({
                'success': True,
                'babies': babies,
                'count': len(babies)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ['name', 'birth_date', 'gender']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Validate name
            if len(data['name'].strip()) < 2:
                return jsonify({'error': 'Baby name must be at least 2 characters long'}), 400

            # Validate gender
            if data['gender'].lower() not in ['male', 'female', 'other']:
                return jsonify({'error': 'Gender must be male, female, or other'}), 400

            # Validate birth date
            try:
                birth_date_obj = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                if birth_date_obj > date.today():
                    return jsonify({'error': 'Birth date cannot be in the future'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

            # Create baby
            baby_dict = {
                'name': data['name'].strip(),
                'birth_date': data['birth_date'],
                'gender': data['gender'].lower(),
                'parent_id': session['user_id'],
                'weight_at_birth': data.get('weight_at_birth'),
                'height_at_birth': data.get('height_at_birth'),
                'blood_type': data.get('blood_type'),
                'notes': data.get('notes', '')
            }
            
            baby_data = DataManager.create_baby(baby_dict)

            if not baby_data:
                return jsonify({'error': 'Failed to create baby'}), 500

            return jsonify({
                'success': True,
                'message': 'Baby registered successfully',
                'baby': baby_data
            }), 201

        except Exception as e:
            return jsonify({'error': f'Failed to register baby: {str(e)}'}), 500

@demo_bp.route('/api/babies/<int:baby_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def baby_detail_api(baby_id):
    """Get, update, or delete a specific baby"""
    try:
        user_data = DataManager.get_user_by_id(session['user_id'])
        baby_data = DataManager.get_baby_by_id(baby_id)

        if not baby_data:
            return jsonify({'error': 'Baby not found'}), 404

        # Check access permissions
        if baby_data['parent_id'] != session['user_id'] and user_data['role'] != 'admin':
            return jsonify({'error': 'Access denied'}), 403

        if request.method == 'GET':
            return jsonify({
                'success': True,
                'baby': baby_data
            })

        elif request.method == 'PUT':
            data = request.get_json()
            updates = {}

            # Validate and prepare updates
            if 'name' in data:
                if len(data['name'].strip()) < 2:
                    return jsonify({'error': 'Baby name must be at least 2 characters long'}), 400
                updates['name'] = data['name'].strip()

            if 'birth_date' in data:
                try:
                    birth_date_obj = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                    if birth_date_obj > date.today():
                        return jsonify({'error': 'Birth date cannot be in the future'}), 400
                    updates['birth_date'] = data['birth_date']
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

            if 'gender' in data:
                if data['gender'].lower() not in ['male', 'female', 'other']:
                    return jsonify({'error': 'Gender must be male, female, or other'}), 400
                updates['gender'] = data['gender'].lower()

            for field in ['weight_at_birth', 'height_at_birth', 'blood_type', 'notes']:
                if field in data:
                    updates[field] = data[field]

            # Update baby
            if DataManager.update_baby(baby_id, updates):
                updated_baby = DataManager.get_baby_by_id(baby_id)
                return jsonify({
                    'success': True,
                    'message': 'Baby information updated successfully',
                    'baby': updated_baby
                })
            else:
                return jsonify({'error': 'Failed to update baby'}), 500

        elif request.method == 'DELETE':
            # Soft delete - mark as inactive
            if DataManager.update_baby(baby_id, {'is_active': False}):
                return jsonify({
                    'success': True,
                    'message': 'Baby record deactivated successfully'
                })
            else:
                return jsonify({'error': 'Failed to deactivate baby'}), 500

    except Exception as e:
        return jsonify({'error': f'Operation failed: {str(e)}'}), 500

@demo_bp.route('/api/admin/update-content', methods=['POST'])
def demo_update_content():
    """Demo content update"""
    return jsonify({
        'success': True,
        'message': 'Content updated successfully (demo mode)'
    })

# Mock authentication for demo
@demo_bp.route('/api/check-auth')
def demo_check_auth():
    """Demo authentication check"""
    return jsonify({
        'authenticated': True,
        'user': {
            'id': 1,
            'name': 'Demo Admin',
            'email': 'admin@demo.com',
            'role': 'admin'
        }
    })

@demo_bp.route('/api/user-data')
def demo_user_data():
    """Demo user data"""
    return jsonify({
        'success': True,
        'user': {
            'id': 1,
            'name': 'Demo Admin',
            'email': 'admin@demo.com',
            'role': 'admin'
        }
    })

# Nutrition API Endpoints

@demo_bp.route('/api/nutrition', methods=['GET', 'POST'])
@login_required
def nutrition_api():
    """Get nutrition records for current user or create a new record"""
    if request.method == 'GET':
        try:
            user_data = DataManager.get_user_by_id(session['user_id'])
            is_admin = user_data['role'] == 'admin'

            # Get all nutrition records (simplified for demo)
            data = DataManager.get_data()
            nutrition_records = data.get('nutrition_records', [])

            if not is_admin:
                # Filter by user's babies
                user_babies = DataManager.get_babies_for_user(session['user_id'])
                baby_ids = [baby['id'] for baby in user_babies]
                nutrition_records = [r for r in nutrition_records if r['baby_id'] in baby_ids]

            return jsonify({
                'success': True,
                'records': nutrition_records
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data_input = request.get_json()

            # Validate required fields
            required_fields = ['baby_id', 'record_date', 'feeding_type']
            for field in required_fields:
                if field not in data_input or not data_input[field]:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Verify baby access
            baby_data = DataManager.get_baby_by_id(data_input['baby_id'])
            if not baby_data:
                return jsonify({'error': 'Baby not found'}), 404

            user_data = DataManager.get_user_by_id(session['user_id'])
            if baby_data['parent_id'] != session['user_id'] and user_data['role'] != 'admin':
                return jsonify({'error': 'Access denied'}), 403

            # Create nutrition record
            data = DataManager.get_data()
            new_id = max([r['id'] for r in data['nutrition_records']], default=0) + 1

            nutrition_record = {
                'id': new_id,
                'baby_id': data_input['baby_id'],
                'record_date': data_input['record_date'],
                'feeding_type': data_input['feeding_type'],
                'amount': data_input.get('amount'),
                'duration': data_input.get('duration'),
                'food_items': data_input.get('food_items'),
                'appetite_level': data_input.get('appetite_level'),
                'allergic_reactions': data_input.get('allergic_reactions'),
                'notes': data_input.get('notes', ''),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            data['nutrition_records'].append(nutrition_record)

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Nutrition record saved successfully',
                    'record': nutrition_record
                }), 201
            else:
                return jsonify({'error': 'Failed to save nutrition record'}), 500

        except Exception as e:
            return jsonify({'error': f'Failed to save nutrition record: {str(e)}'}), 500

@demo_bp.route('/api/nutrition/<int:baby_id>')
@login_required
def nutrition_by_baby(baby_id):
    """Get nutrition records for a specific baby"""
    try:
        # Verify baby access
        baby_data = DataManager.get_baby_by_id(baby_id)
        if not baby_data:
            return jsonify({'error': 'Baby not found'}), 404

        user_data = DataManager.get_user_by_id(session['user_id'])
        if baby_data['parent_id'] != session['user_id'] and user_data['role'] != 'admin':
            return jsonify({'error': 'Access denied'}), 403

        # Get nutrition records for this baby
        data = DataManager.get_data()
        nutrition_records = [r for r in data.get('nutrition_records', []) if r['baby_id'] == baby_id]

        # Sort by date (newest first)
        nutrition_records.sort(key=lambda x: x['record_date'], reverse=True)

        return jsonify({
            'success': True,
            'records': nutrition_records
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vaccination API Endpoints

@demo_bp.route('/api/vaccinations', methods=['GET', 'POST'])
@login_required
def vaccinations_api():
    """Get vaccination records for current user or create a new record"""
    if request.method == 'GET':
        try:
            user_data = DataManager.get_user_by_id(session['user_id'])
            is_admin = user_data['role'] == 'admin'

            # Get all vaccination records (simplified for demo)
            data = DataManager.get_data()
            vaccination_records = data.get('vaccinations', [])

            if not is_admin:
                # Filter by user's babies
                user_babies = DataManager.get_babies_for_user(session['user_id'])
                baby_ids = [baby['id'] for baby in user_babies]
                vaccination_records = [r for r in vaccination_records if r['baby_id'] in baby_ids]

            return jsonify({
                'success': True,
                'records': vaccination_records
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data_input = request.get_json()

            # Validate required fields
            required_fields = ['baby_id', 'vaccine_name', 'scheduled_date']
            for field in required_fields:
                if field not in data_input or not data_input[field]:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Verify baby access
            baby_data = DataManager.get_baby_by_id(data_input['baby_id'])
            if not baby_data:
                return jsonify({'error': 'Baby not found'}), 404

            user_data = DataManager.get_user_by_id(session['user_id'])
            if baby_data['parent_id'] != session['user_id'] and user_data['role'] != 'admin':
                return jsonify({'error': 'Access denied'}), 403

            # Create vaccination record
            data = DataManager.get_data()
            new_id = max([r['id'] for r in data['vaccinations']], default=0) + 1

            vaccination_record = {
                'id': new_id,
                'baby_id': data_input['baby_id'],
                'vaccine_name': data_input['vaccine_name'],
                'vaccine_type': data_input.get('vaccine_type', 'routine'),
                'scheduled_date': data_input['scheduled_date'],
                'administered_date': data_input.get('administered_date'),
                'status': data_input.get('status', 'scheduled'),
                'doctor_name': data_input.get('doctor_name'),
                'clinic_name': data_input.get('clinic_name'),
                'batch_number': data_input.get('batch_number'),
                'side_effects': data_input.get('side_effects'),
                'notes': data_input.get('notes', ''),
                'reminder_sent': False,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            data['vaccinations'].append(vaccination_record)

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Vaccination scheduled successfully',
                    'record': vaccination_record
                }), 201
            else:
                return jsonify({'error': 'Failed to schedule vaccination'}), 500

        except Exception as e:
            return jsonify({'error': f'Failed to schedule vaccination: {str(e)}'}), 500

@demo_bp.route('/api/vaccinations/<int:baby_id>')
@login_required
def vaccinations_by_baby(baby_id):
    """Get vaccination records for a specific baby"""
    try:
        # Verify baby access
        baby_data = DataManager.get_baby_by_id(baby_id)
        if not baby_data:
            return jsonify({'error': 'Baby not found'}), 404

        user_data = DataManager.get_user_by_id(session['user_id'])
        if baby_data['parent_id'] != session['user_id'] and user_data['role'] != 'admin':
            return jsonify({'error': 'Access denied'}), 403

        # Get vaccination records for this baby
        data = DataManager.get_data()
        vaccination_records = [r for r in data.get('vaccinations', []) if r['baby_id'] == baby_id]

        # Sort by scheduled date
        vaccination_records.sort(key=lambda x: x['scheduled_date'])

        return jsonify({
            'success': True,
            'records': vaccination_records
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@demo_bp.route('/api/vaccinations/<int:vaccination_id>', methods=['PUT', 'DELETE'])
@login_required
def vaccination_detail(vaccination_id):
    """Update or delete a specific vaccination"""
    try:
        data = DataManager.get_data()
        vaccination_record = None
        vaccination_index = None

        for i, record in enumerate(data.get('vaccinations', [])):
            if record['id'] == vaccination_id:
                vaccination_record = record
                vaccination_index = i
                break

        if not vaccination_record:
            return jsonify({'error': 'Vaccination not found'}), 404

        # Verify access
        baby_data = DataManager.get_baby_by_id(vaccination_record['baby_id'])
        user_data = DataManager.get_user_by_id(session['user_id'])
        if baby_data['parent_id'] != session['user_id'] and user_data['role'] != 'admin':
            return jsonify({'error': 'Access denied'}), 403

        if request.method == 'PUT':
            update_data = request.get_json()

            # Update fields
            for field in ['status', 'administered_date', 'scheduled_date', 'doctor_name', 'clinic_name', 'notes', 'side_effects']:
                if field in update_data:
                    vaccination_record[field] = update_data[field]

            vaccination_record['updated_at'] = datetime.utcnow().isoformat()

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Vaccination updated successfully',
                    'record': vaccination_record
                })
            else:
                return jsonify({'error': 'Failed to update vaccination'}), 500

        elif request.method == 'DELETE':
            data['vaccinations'].pop(vaccination_index)

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Vaccination deleted successfully'
                })
            else:
                return jsonify({'error': 'Failed to delete vaccination'}), 500

    except Exception as e:
        return jsonify({'error': f'Operation failed: {str(e)}'}), 500

# Growth API Endpoints

@demo_bp.route('/api/growth', methods=['GET', 'POST'])
@login_required
def growth_api():
    """Get growth records for current user or create a new record"""
    if request.method == 'GET':
        try:
            user_data = DataManager.get_user_by_id(session['user_id'])
            is_admin = user_data['role'] == 'admin'

            # Get all growth records (simplified for demo)
            data = DataManager.get_data()
            growth_records = data.get('growth_records', [])

            if not is_admin:
                # Filter by user's babies
                user_babies = DataManager.get_babies_for_user(session['user_id'])
                baby_ids = [baby['id'] for baby in user_babies]
                growth_records = [r for r in growth_records if r['baby_id'] in baby_ids]

            return jsonify({
                'success': True,
                'records': growth_records
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data_input = request.get_json()

            # Validate required fields
            required_fields = ['baby_id', 'record_date']
            for field in required_fields:
                if field not in data_input or not data_input[field]:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Verify baby access
            baby_data = DataManager.get_baby_by_id(data_input['baby_id'])
            if not baby_data:
                return jsonify({'error': 'Baby not found'}), 404

            user_data = DataManager.get_user_by_id(session['user_id'])
            if baby_data['parent_id'] != session['user_id'] and user_data['role'] != 'admin':
                return jsonify({'error': 'Access denied'}), 403

            # Calculate BMI if weight and height are provided
            bmi = None
            if data_input.get('weight') and data_input.get('height'):
                weight = float(data_input['weight'])
                height = float(data_input['height']) / 100  # convert cm to meters
                bmi = round(weight / (height ** 2), 2)

            # Create growth record
            data = DataManager.get_data()
            new_id = max([r['id'] for r in data['growth_records']], default=0) + 1

            growth_record = {
                'id': new_id,
                'baby_id': data_input['baby_id'],
                'record_date': data_input['record_date'],
                'weight': data_input.get('weight'),
                'height': data_input.get('height'),
                'head_circumference': data_input.get('head_circumference'),
                'chest_circumference': data_input.get('chest_circumference'),
                'bmi': bmi,
                'percentile_weight': data_input.get('percentile_weight'),
                'percentile_height': data_input.get('percentile_height'),
                'doctor_name': data_input.get('doctor_name'),
                'notes': data_input.get('notes', ''),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            data['growth_records'].append(growth_record)

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Growth record saved successfully',
                    'record': growth_record
                }), 201
            else:
                return jsonify({'error': 'Failed to save growth record'}), 500

        except Exception as e:
            return jsonify({'error': f'Failed to save growth record: {str(e)}'}), 500

@demo_bp.route('/api/growth/<int:baby_id>')
@login_required
def growth_by_baby(baby_id):
    """Get growth records for a specific baby"""
    try:
        # Verify baby access
        baby_data = DataManager.get_baby_by_id(baby_id)
        if not baby_data:
            return jsonify({'error': 'Baby not found'}), 404

        user_data = DataManager.get_user_by_id(session['user_id'])
        if baby_data['parent_id'] != session['user_id'] and user_data['role'] != 'admin':
            return jsonify({'error': 'Access denied'}), 403

        # Get growth records for this baby
        data = DataManager.get_data()
        growth_records = [r for r in data.get('growth_records', []) if r['baby_id'] == baby_id]

        # Sort by date (newest first)
        growth_records.sort(key=lambda x: x['record_date'], reverse=True)

        return jsonify({
            'success': True,
            'records': growth_records
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User management routes moved to admin.py to avoid conflicts

# Admin Routes

@demo_bp.route('/admin/users')
@admin_required
def admin_users_page():
    """Admin users management page"""
    return render_template('admin/users.html')

@demo_bp.route('/admin/babies')
@admin_required
def admin_babies_page():
    """Admin babies management page"""
    return render_template('admin/babies.html')

@demo_bp.route('/admin/reports')
@admin_required
def admin_reports_page():
    """Admin reports page"""
    return render_template('admin/reports.html')

@demo_bp.route('/admin/settings')
@admin_required
def admin_settings_page():
    """Admin settings page"""
    return render_template('admin/settings.html')

@demo_bp.route('/admin/manage-exercises')
@admin_required
def admin_exercises_page():
    """Admin exercises management page"""
    return render_template('admin/manage_exercises.html')

@demo_bp.route('/admin/manage-faq')
@admin_required
def admin_faq_page():
    """Admin FAQ management page"""
    return render_template('admin/manage_faq.html')

@demo_bp.route('/admin/manage-schemes')
@admin_required
def admin_schemes_page():
    """Admin schemes management page"""
    return render_template('admin/manage_schemes.html')

# Admin API Endpoints for Exercises

@demo_bp.route('/admin/api/exercises', methods=['GET', 'POST'])
@admin_required
def admin_exercises_api():
    """Get all exercises or create a new exercise"""
    if request.method == 'GET':
        try:
            data = DataManager.get_data()
            exercises = data.get('exercises', [])
            return jsonify({
                'success': True,
                'exercises': exercises
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data_input = request.get_json()

            # Validate required fields
            required_fields = ['name', 'category', 'difficulty']
            for field in required_fields:
                if field not in data_input or not data_input[field]:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Create exercise
            data = DataManager.get_data()
            new_id = max([e['id'] for e in data.get('exercises', [])], default=0) + 1

            exercise = {
                'id': new_id,
                'name': data_input['name'],
                'category': data_input['category'],
                'difficulty': data_input['difficulty'],
                'duration': data_input.get('duration'),
                'description': data_input.get('description', ''),
                'instructions': data_input.get('instructions', ''),
                'precautions': data_input.get('precautions', ''),
                'benefits': data_input.get('benefits', ''),
                'trimester': data_input.get('trimester'),
                'equipment': data_input.get('equipment', ''),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            if 'exercises' not in data:
                data['exercises'] = []
            data['exercises'].append(exercise)

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Exercise created successfully',
                    'exercise': exercise
                }), 201
            else:
                return jsonify({'error': 'Failed to save exercise'}), 500

        except Exception as e:
            return jsonify({'error': f'Failed to create exercise: {str(e)}'}), 500

@demo_bp.route('/admin/api/exercises/<int:exercise_id>', methods=['PUT', 'DELETE'])
@admin_required
def admin_exercise_detail(exercise_id):
    """Update or delete a specific exercise"""
    try:
        data = DataManager.get_data()
        exercise_record = None
        exercise_index = None

        for i, exercise in enumerate(data.get('exercises', [])):
            if exercise['id'] == exercise_id:
                exercise_record = exercise
                exercise_index = i
                break

        if not exercise_record:
            return jsonify({'error': 'Exercise not found'}), 404

        if request.method == 'PUT':
            update_data = request.get_json()

            # Update fields
            for field in ['name', 'category', 'difficulty', 'duration', 'description', 'instructions', 'precautions', 'benefits', 'trimester', 'equipment']:
                if field in update_data:
                    exercise_record[field] = update_data[field]

            exercise_record['updated_at'] = datetime.utcnow().isoformat()

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Exercise updated successfully',
                    'exercise': exercise_record
                })
            else:
                return jsonify({'error': 'Failed to update exercise'}), 500

        elif request.method == 'DELETE':
            data['exercises'].pop(exercise_index)

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Exercise deleted successfully'
                })
            else:
                return jsonify({'error': 'Failed to delete exercise'}), 500

    except Exception as e:
        return jsonify({'error': f'Operation failed: {str(e)}'}), 500

# Admin API Endpoints for FAQs

@demo_bp.route('/admin/api/faqs', methods=['GET', 'POST'])
@admin_required
def admin_faqs_api():
    """Get all FAQs or create a new FAQ"""
    if request.method == 'GET':
        try:
            data = DataManager.get_data()
            faqs = data.get('faqs', [])
            return jsonify({
                'success': True,
                'faqs': faqs
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data_input = request.get_json()

            # Validate required fields
            required_fields = ['question', 'answer', 'category']
            for field in required_fields:
                if field not in data_input or not data_input[field]:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Create FAQ
            data = DataManager.get_data()
            new_id = max([f['id'] for f in data.get('faqs', [])], default=0) + 1

            faq = {
                'id': new_id,
                'question': data_input['question'],
                'answer': data_input['answer'],
                'category': data_input['category'],
                'tags': data_input.get('tags', ''),
                'priority': data_input.get('priority', 'medium'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            if 'faqs' not in data:
                data['faqs'] = []
            data['faqs'].append(faq)

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'FAQ created successfully',
                    'faq': faq
                }), 201
            else:
                return jsonify({'error': 'Failed to save FAQ'}), 500

        except Exception as e:
            return jsonify({'error': f'Failed to create FAQ: {str(e)}'}), 500

@demo_bp.route('/admin/api/faqs/<int:faq_id>', methods=['PUT', 'DELETE'])
@admin_required
def admin_faq_detail(faq_id):
    """Update or delete a specific FAQ"""
    try:
        data = DataManager.get_data()
        faq_record = None
        faq_index = None

        for i, faq in enumerate(data.get('faqs', [])):
            if faq['id'] == faq_id:
                faq_record = faq
                faq_index = i
                break

        if not faq_record:
            return jsonify({'error': 'FAQ not found'}), 404

        if request.method == 'PUT':
            update_data = request.get_json()

            # Update fields
            for field in ['question', 'answer', 'category', 'tags', 'priority']:
                if field in update_data:
                    faq_record[field] = update_data[field]

            faq_record['updated_at'] = datetime.utcnow().isoformat()

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'FAQ updated successfully',
                    'faq': faq_record
                })
            else:
                return jsonify({'error': 'Failed to update FAQ'}), 500

        elif request.method == 'DELETE':
            data['faqs'].pop(faq_index)

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'FAQ deleted successfully'
                })
            else:
                return jsonify({'error': 'Failed to delete FAQ'}), 500

    except Exception as e:
        return jsonify({'error': f'Operation failed: {str(e)}'}), 500

# Admin API Endpoints for Schemes

@demo_bp.route('/admin/api/schemes', methods=['GET', 'POST'])
@admin_required
def admin_schemes_api():
    """Get all schemes or create a new scheme"""
    if request.method == 'GET':
        try:
            data = DataManager.get_data()
            schemes = data.get('schemes', [])
            return jsonify({
                'success': True,
                'schemes': schemes
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data_input = request.get_json()

            # Validate required fields
            required_fields = ['name', 'category', 'description']
            for field in required_fields:
                if field not in data_input or not data_input[field]:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Create scheme
            data = DataManager.get_data()
            new_id = max([s['id'] for s in data.get('schemes', [])], default=0) + 1

            scheme = {
                'id': new_id,
                'name': data_input['name'],
                'category': data_input['category'],
                'description': data_input['description'],
                'eligibility': data_input.get('eligibility', ''),
                'benefits': data_input.get('benefits', ''),
                'application_process': data_input.get('application_process', ''),
                'required_documents': data_input.get('required_documents', ''),
                'website': data_input.get('website', ''),
                'contact': data_input.get('contact', ''),
                'amount': data_input.get('amount', ''),
                'status': data_input.get('status', 'active'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            if 'schemes' not in data:
                data['schemes'] = []
            data['schemes'].append(scheme)

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Scheme created successfully',
                    'scheme': scheme
                }), 201
            else:
                return jsonify({'error': 'Failed to save scheme'}), 500

        except Exception as e:
            return jsonify({'error': f'Failed to create scheme: {str(e)}'}), 500

@demo_bp.route('/admin/api/schemes/<int:scheme_id>', methods=['PUT', 'DELETE'])
@admin_required
def admin_scheme_detail(scheme_id):
    """Update or delete a specific scheme"""
    try:
        data = DataManager.get_data()
        scheme_record = None
        scheme_index = None

        for i, scheme in enumerate(data.get('schemes', [])):
            if scheme['id'] == scheme_id:
                scheme_record = scheme
                scheme_index = i
                break

        if not scheme_record:
            return jsonify({'error': 'Scheme not found'}), 404

        if request.method == 'PUT':
            update_data = request.get_json()

            # Update fields
            for field in ['name', 'category', 'description', 'eligibility', 'benefits', 'application_process', 'required_documents', 'website', 'contact', 'amount', 'status']:
                if field in update_data:
                    scheme_record[field] = update_data[field]

            scheme_record['updated_at'] = datetime.utcnow().isoformat()

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Scheme updated successfully',
                    'scheme': scheme_record
                })
            else:
                return jsonify({'error': 'Failed to update scheme'}), 500

        elif request.method == 'DELETE':
            data['schemes'].pop(scheme_index)

            if DataManager.save_data(data):
                return jsonify({
                    'success': True,
                    'message': 'Scheme deleted successfully'
                })
            else:
                return jsonify({'error': 'Failed to delete scheme'}), 500

    except Exception as e:
        return jsonify({'error': f'Operation failed: {str(e)}'}), 500
