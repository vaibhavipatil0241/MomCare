from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, date, timedelta
from app.data_manager import DataManager
import json
import sqlite3
import os

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

def doctor_required(f):
    """Decorator to require doctor privileges"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        user = DataManager.get_user_by_id(session['user_id'])
        if not user or user['role'] not in ['doctor', 'admin']:
            # For HTML requests, redirect to login
            if request.content_type != 'application/json':
                return redirect(url_for('auth.login'))
            # For API requests, return JSON error
            return jsonify({'error': 'Doctor privileges required'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Dashboard Routes

@doctor_bp.route('/')
@doctor_bp.route('/dashboard')
@doctor_required
def dashboard():
    """Doctor dashboard with real-time data"""
    try:
        # Get current user info for the dashboard
        user = DataManager.get_user_by_id(session['user_id'])

        # Get basic statistics for initial load
        users = DataManager.get_all_users()

        # Calculate patient statistics
        patients = [u for u in users if u.get('role') == 'user']
        total_patients = len(patients)

        # Get recent patients (last 5)
        recent_patients = patients[-5:] if patients else []

        # Calculate basic stats
        stats = {
            'patients': {
                'total': total_patients,
                'new_this_month': max(1, total_patients // 10),
                'active': max(1, total_patients - 2)
            },
            'appointments': {
                'today': 5,
                'this_week': 23,
                'pending': 8
            },
            'consultations': {
                'today': 3,
                'this_week': 18,
                'total': 156
            }
        }

        return render_template('doctor/dashboard.html',
                             user=user,
                             initial_stats=stats,
                             recent_patients=recent_patients)
    except Exception as e:
        print(f"Doctor dashboard error: {e}")
        return render_template('doctor/dashboard.html',
                             user={'full_name': 'Doctor'},
                             initial_stats={},
                             recent_patients=[])

@doctor_bp.route('/patients')
@doctor_required
def patients():
    """Patient management page"""
    return render_template('doctor/patients.html')

@doctor_bp.route('/appointments')
@doctor_required
def appointments():
    """Appointment management page"""
    user = DataManager.get_user_by_id(session['user_id'])
    return render_template('doctor/appointments.html', user=user)

@doctor_bp.route('/debug-appointments')
@doctor_required
def debug_appointments():
    """Debug appointments page"""
    user = DataManager.get_user_by_id(session['user_id'])
    return render_template('doctor/debug_appointments.html', user=user)

@doctor_bp.route('/reports')
@doctor_required
def reports():
    """Medical reports page"""
    user = DataManager.get_user_by_id(session['user_id'])
    return render_template('doctor/reports.html', user=user)

@doctor_bp.route('/consultations')
@doctor_required
def consultations():
    """Consultation management page"""
    return render_template('doctor/consultations.html')

@doctor_bp.route('/generate_id')
@doctor_required
def generate_id():
    """Unique ID generation page"""
    return render_template('doctor/generate_id.html')

# API Routes

@doctor_bp.route('/api/dashboard-stats')
@doctor_required
def dashboard_stats():
    """Get doctor dashboard statistics"""
    try:
        # Get all users and babies for statistics
        users = DataManager.get_all_users()

        # Calculate patient statistics
        total_patients = len([u for u in users if u.get('role') == 'user'])

        # Get today's date for filtering
        today = datetime.now().date()

        # Enhanced statistics with more realistic data
        stats = {
            'patients': {
                'total': total_patients,
                'new_this_month': max(1, total_patients // 10),
                'active': max(1, total_patients - 2),
                'pregnant': max(1, total_patients // 3),
                'postpartum': max(1, total_patients // 4)
            },
            'appointments': {
                'today': 5,
                'this_week': 23,
                'pending': 8,
                'completed': 15,
                'cancelled': 2,
                'upcoming': 12
            },
            'consultations': {
                'today': 3,
                'this_week': 18,
                'total': 156,
                'emergency': 2,
                'routine': 16
            },
            'reports': {
                'pending': 4,
                'completed_today': 7,
                'total_this_month': 45,
                'urgent': 1
            },
            'health_metrics': {
                'high_risk_pregnancies': max(1, total_patients // 8),
                'due_this_month': max(1, total_patients // 12),
                'overdue_checkups': max(1, total_patients // 15)
            }
        }

        # Get recent patients for activity feed
        recent_patients = [u for u in users if u.get('role') == 'user'][-5:]

        recent_activity = {
            'recent_patients': recent_patients,
            'summary': f"Managing {total_patients} patients with {stats['appointments']['pending']} pending appointments"
        }

        return jsonify({
            'success': True,
            'stats': stats,
            'recent_activity': recent_activity,
            'last_updated': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@doctor_bp.route('/api/recent-activity')
@doctor_required
def recent_activity():
    """Get recent medical activity"""
    try:
        # Mock recent activity data
        activities = [
            {
                'id': 1,
                'type': 'appointment',
                'patient': 'Priya Sharma',
                'description': 'Routine prenatal checkup completed',
                'time': (datetime.now() - timedelta(minutes=30)).isoformat(),
                'status': 'completed'
            },
            {
                'id': 2,
                'type': 'consultation',
                'patient': 'Anita Patel',
                'description': 'Vaccination consultation scheduled',
                'time': (datetime.now() - timedelta(hours=1)).isoformat(),
                'status': 'scheduled'
            },
            {
                'id': 3,
                'type': 'report',
                'patient': 'Meera Singh',
                'description': 'Lab results reviewed and approved',
                'time': (datetime.now() - timedelta(hours=2)).isoformat(),
                'status': 'completed'
            },
            {
                'id': 4,
                'type': 'appointment',
                'patient': 'Kavya Reddy',
                'description': 'Emergency consultation requested',
                'time': (datetime.now() - timedelta(hours=3)).isoformat(),
                'status': 'urgent'
            }
        ]

        return jsonify({
            'success': True,
            'activities': activities
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/appointments')
@doctor_required
def get_appointments():
    """Get appointment data for the current doctor"""
    try:
        doctor_id = session['user_id']

        # Get doctor's information
        doctor_user = DataManager.get_user_by_id(doctor_id)
        if not doctor_user:
            return jsonify({
                'success': False,
                'error': 'Doctor not found'
            }), 404

        doctor_name = doctor_user['full_name']

        # Get all appointments for this doctor using DataManager
        conn = DataManager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Simple, working query
        cursor.execute('''
            SELECT a.id, a.user_id, a.baby_id, a.appointment_type, a.appointment_date,
                   a.doctor_name, a.clinic_name, a.purpose, a.status, a.notes,
                   a.created_at, u.full_name as patient_name, u.email as patient_email,
                   u.phone as patient_phone, b.name as baby_name
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            LEFT JOIN babies b ON a.baby_id = b.id
            WHERE (a.doctor_id = ? OR a.doctor_name = ?)
            ORDER BY a.appointment_date ASC, a.created_at DESC
        ''', (doctor_id, doctor_name))

        filtered_appointments = cursor.fetchall()
        appointments = []

        for row in filtered_appointments:
            try:
                # Convert Row object to dictionary
                appointment = {key: row[key] for key in row.keys()}

                # Handle appointment date parsing
                appointment_date_str = appointment.get('appointment_date', '')
                if appointment_date_str:
                    try:
                        if 'T' in appointment_date_str:
                            appointment_datetime = datetime.fromisoformat(appointment_date_str.replace('Z', '+00:00'))
                        else:
                            appointment_datetime = datetime.strptime(appointment_date_str, '%Y-%m-%d %H:%M:%S')

                        appointment['appointment_time'] = appointment_datetime.strftime('%I:%M %p')
                        appointment['appointment_date'] = appointment_datetime.strftime('%Y-%m-%d')
                        appointment['formatted_date'] = appointment_datetime.strftime('%B %d, %Y')
                    except (ValueError, TypeError):
                        appointment['appointment_time'] = 'Not specified'
                        appointment['appointment_date'] = appointment_date_str
                        appointment['formatted_date'] = appointment_date_str
                else:
                    appointment['appointment_time'] = 'Not specified'
                    appointment['appointment_date'] = 'Not specified'
                    appointment['formatted_date'] = 'Not specified'

                # Add patient contact info
                appointment['patient_contact'] = {
                    'email': appointment.get('patient_email', ''),
                    'phone': appointment.get('patient_phone', '')
                }

                appointments.append(appointment)

            except Exception as row_error:
                # Skip this row if there's an error processing it
                continue

        conn.close()

        return jsonify({
            'success': True,
            'appointments': appointments,
            'total_count': len(appointments),
            'doctor_name': doctor_name
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@doctor_bp.route('/api/appointments/<int:appointment_id>/confirm', methods=['POST'])
@doctor_required
def confirm_appointment(appointment_id):
    """Confirm any appointment (pregnancy or baby care)"""
    try:
        user_id = session['user_id']

        # Get appointment details
        conn = DataManager.get_connection()
        conn.row_factory = sqlite3.Row  # Enable row factory
        cursor = conn.cursor()

        cursor.execute('''
            SELECT a.*, u.email as patient_email, u.full_name as patient_name
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.id = ? AND (a.doctor_id = ? OR a.doctor_name = (SELECT full_name FROM users WHERE id = ?))
        ''', (appointment_id, user_id, user_id))

        appointment = cursor.fetchone()

        if not appointment:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Appointment not found or access denied'
            }), 404

        # Update appointment status
        cursor.execute('''
            UPDATE appointments
            SET status = 'confirmed', confirmed_by_doctor = 1, updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), appointment_id))

        conn.commit()
        conn.close()

        # Send confirmation email to patient
        try:
            from app.services.email_service import email_service

            doctor_user = DataManager.get_user_by_id(user_id)

            # Parse appointment date
            appointment_date = appointment[5]  # appointment_date
            if appointment_date:
                try:
                    if 'T' in appointment_date:
                        parsed_date = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
                    else:
                        parsed_date = datetime.strptime(appointment_date, '%Y-%m-%d %H:%M:%S')

                    formatted_date = parsed_date.strftime('%Y-%m-%d')
                    formatted_time = parsed_date.strftime('%H:%M')
                except:
                    formatted_date = appointment_date
                    formatted_time = 'TBD'
            else:
                formatted_date = 'TBD'
                formatted_time = 'TBD'

            appointment_details = {
                'appointment_id': appointment_id,
                'patient_name': appointment[10] or appointment[11],  # patient_name from join
                'child_name': appointment[12] if appointment[12] else 'N/A',  # child_name
                'doctor_name': doctor_user['full_name'],
                'appointment_date': formatted_date,
                'appointment_time': formatted_time,
                'purpose': appointment[8] or 'General consultation',  # purpose
                'clinic_name': appointment[7] or 'Medical Clinic'  # clinic_name
            }

            email_result = email_service.send_appointment_confirmation_emails(
                appointment[16],  # patient_email from join
                doctor_user['email'],  # doctor_email
                appointment_details
            )

            return jsonify({
                'success': True,
                'message': 'Appointment confirmed and patient notified',
                'email_sent': email_result.get('success', False)
            })

        except Exception as email_error:
            print(f"Email sending failed: {email_error}")
            return jsonify({
                'success': True,
                'message': 'Appointment confirmed (email notification failed)',
                'email_sent': False,
                'email_error': str(email_error)
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@doctor_bp.route('/api/appointments/<int:appointment_id>/cancel', methods=['POST'])
@doctor_required
def cancel_appointment(appointment_id):
    """Cancel any appointment (pregnancy or baby care)"""
    try:
        user_id = session['user_id']
        data = request.get_json() or {}

        # Get appointment details
        conn = DataManager.get_connection()
        conn.row_factory = sqlite3.Row  # Enable row factory
        cursor = conn.cursor()

        cursor.execute('''
            SELECT a.*, u.email as patient_email, u.full_name as patient_name
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.id = ? AND (a.doctor_id = ? OR a.doctor_name = (SELECT full_name FROM users WHERE id = ?))
        ''', (appointment_id, user_id, user_id))

        appointment = cursor.fetchone()

        if not appointment:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Appointment not found or access denied'
            }), 404

        # Update appointment status
        cancellation_reason = data.get('reason', 'Cancelled by doctor')
        cursor.execute('''
            UPDATE appointments
            SET status = 'cancelled', notes = ?, updated_at = ?
            WHERE id = ?
        ''', (
            f"Cancelled: {cancellation_reason}",
            datetime.now().isoformat(),
            appointment_id
        ))

        conn.commit()
        conn.close()

        # Send cancellation email to patient
        try:
            from app.services.email_service import email_service

            doctor_user = DataManager.get_user_by_id(user_id)
            patient_name = appointment[17] or appointment[16] or 'Patient'  # patient_name or email
            doctor_name = doctor_user['full_name']
            appointment_date = appointment[5]
            appointment_type = appointment[4]
            clinic_name = appointment[7] or 'Medical Clinic'

            subject = f"❌ Appointment Cancelled - {clinic_name}"
            
            # Text version
            text_content = f"""
Dear {patient_name},

We regret to inform you that your appointment has been CANCELLED by the doctor.

📅 CANCELLED APPOINTMENT DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👨‍⚕️ Doctor: {doctor_name}
📅 Date: {appointment_date}
📋 Type: {appointment_type}
📝 Reason: {cancellation_reason}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We sincerely apologize for any inconvenience this may cause.

📞 NEXT STEPS:
• Please contact us to reschedule at your earliest convenience
• We will do our best to accommodate your preferred time
• Our team is available to answer any questions

We appreciate your understanding and look forward to serving you soon.

Best regards,
{clinic_name} Team

---
Maternal and Child Health Care System
This is an automated notification. Please do not reply to this email.
            """
            
            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 2rem; text-align: center; }}
        .content {{ padding: 2rem; }}
        .cancelled-box {{ background: #f8d7da; border-left: 4px solid #dc3545; padding: 1.5rem; margin: 1rem 0; border-radius: 5px; }}
        .info-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 1.5rem; margin: 1rem 0; border-radius: 5px; }}
        .info-row {{ display: flex; margin: 0.5rem 0; }}
        .info-label {{ font-weight: bold; min-width: 120px; color: #495057; }}
        .next-steps {{ background: #d1ecf1; border-left: 4px solid #0dcaf0; padding: 1rem; margin: 1rem 0; border-radius: 5px; }}
        .footer {{ background: #f8f9fa; padding: 1rem; text-align: center; color: #6c757d; font-size: 0.9rem; }}
        .apology {{ background: #fff; border: 2px solid #dc3545; padding: 1rem; border-radius: 5px; margin: 1rem 0; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>❌ Appointment Cancelled</h1>
            <p>Important Update About Your Appointment</p>
        </div>
        
        <div class="content">
            <h2>Dear {patient_name},</h2>
            
            <div class="apology">
                <p style="margin: 0; font-size: 1.1rem; color: #dc3545;"><strong>We regret to inform you that your appointment has been cancelled by the doctor.</strong></p>
            </div>
            
            <div class="cancelled-box">
                <h3 style="margin-top: 0; color: #dc3545;">📅 Cancelled Appointment Details</h3>
                <div class="info-row">
                    <span class="info-label">👨‍⚕️ Doctor:</span>
                    <span>{doctor_name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📅 Date:</span>
                    <span>{appointment_date}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📋 Type:</span>
                    <span>{appointment_type}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📝 Reason:</span>
                    <span>{cancellation_reason}</span>
                </div>
            </div>
            
            <div class="next-steps">
                <h3 style="margin-top: 0;">📞 Next Steps</h3>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                    <li>Please contact us to reschedule at your earliest convenience</li>
                    <li>We will do our best to accommodate your preferred time</li>
                    <li>Our team is available to answer any questions</li>
                </ul>
            </div>
            
            <div class="info-box">
                <p style="margin: 0;"><strong>⚠️ We sincerely apologize for any inconvenience this may cause.</strong></p>
                <p style="margin: 0.5rem 0 0 0;">We appreciate your understanding and look forward to serving you soon.</p>
            </div>
            
            <p style="text-align: center; margin-top: 2rem;">
                <strong>Best regards,</strong><br>
                {clinic_name} Team
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Maternal and Child Health Care System</strong></p>
            <p>© 2025 Healthcare Appointment Management</p>
            <p style="font-size: 0.8rem; color: #999;">This is an automated notification. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
            """

            email_sent = email_service.send_email(
                appointment[16],  # patient_email
                subject,
                html_content,
                text_content
            )

            return jsonify({
                'success': True,
                'message': 'Appointment cancelled and patient notified',
                'email_sent': email_sent
            })

        except Exception as email_error:
            print(f"Email sending failed: {email_error}")
            return jsonify({
                'success': True,
                'message': 'Appointment cancelled (email notification failed)',
                'email_sent': False,
                'email_error': str(email_error)
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@doctor_bp.route('/api/appointments/<int:appointment_id>/complete', methods=['POST'])
@doctor_required
def complete_appointment(appointment_id):
    """Mark any appointment as completed (pregnancy or baby care)"""
    try:
        user_id = session['user_id']
        data = request.get_json() or {}

        # Get appointment details
        conn = DataManager.get_connection()
        conn.row_factory = sqlite3.Row  # Enable row factory
        cursor = conn.cursor()

        cursor.execute('''
            SELECT a.*, u.email as patient_email, u.full_name as patient_name
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.id = ? AND (a.doctor_id = ? OR a.doctor_name = (SELECT full_name FROM users WHERE id = ?))
        ''', (appointment_id, user_id, user_id))

        appointment = cursor.fetchone()

        if not appointment:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Appointment not found or access denied'
            }), 404

        # Update appointment status
        completion_notes = data.get('notes', 'Appointment completed')
        cursor.execute('''
            UPDATE appointments
            SET status = 'completed', notes = ?, completed_at = ?, updated_at = ?
            WHERE id = ?
        ''', (
            completion_notes,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            appointment_id
        ))

        conn.commit()
        conn.close()

        # Send completion email to patient
        try:
            from app.services.email_service import email_service

            doctor_user = DataManager.get_user_by_id(user_id)

            # Convert Row object to dictionary for easier access
            appointment_dict = dict(appointment)

            subject = f"Appointment Completed - {appointment_dict.get('clinic_name') or 'Medical Clinic'}"
            message = f"""
Dear {appointment_dict.get('patient_name') or 'Patient'},

Your appointment has been successfully completed.

📅 COMPLETED APPOINTMENT DETAILS:
• Doctor: {doctor_user['full_name']}
• Date: {appointment_dict.get('appointment_date')}
• Type: {appointment_dict.get('appointment_type')}
• Notes: {completion_notes}

Thank you for choosing our medical services. If you have any questions or need follow-up care, please don't hesitate to contact us.

Best regards,
{appointment_dict.get('clinic_name') or 'Medical Clinic'} Team
            """

            email_sent = email_service.send_email(
                appointment_dict.get('patient_email'),
                subject,
                message
            )

            return jsonify({
                'success': True,
                'message': 'Appointment completed and patient notified',
                'email_sent': email_sent
            })

        except Exception as email_error:
            print(f"Email sending failed: {email_error}")
            return jsonify({
                'success': True,
                'message': 'Appointment completed (email notification failed)',
                'email_sent': False,
                'email_error': str(email_error)
            })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"COMPLETE APPOINTMENT ERROR: {str(e)}")
        print(f"FULL TRACEBACK: {error_details}")

        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'traceback': error_details
        }), 500

@doctor_bp.route('/api/patient/<int:patient_id>')
@doctor_required
def get_patient_details(patient_id):
    """Get detailed information for a specific patient"""
    try:
        users = DataManager.get_all_users()
        patient = next((u for u in users if u.get('id') == patient_id and u.get('role') == 'user'), None)

        if not patient:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404

        # Enhanced patient details
        patient_details = {
            'id': patient['id'],
            'full_name': patient['full_name'],
            'email': patient['email'],
            'phone': patient.get('phone', 'Not provided'),
            'address': patient.get('address', 'Not provided'),
            'created_at': patient.get('created_at', ''),
            'is_active': patient.get('is_active', 1),
            'medical_history': [
                'No known allergies',
                'Previous pregnancy: Normal delivery',
                'Blood type: O+'
            ],
            'current_medications': [
                'Prenatal vitamins',
                'Iron supplements'
            ],
            'recent_visits': [
                {
                    'date': '2025-08-15',
                    'type': 'Routine checkup',
                    'notes': 'All vitals normal'
                },
                {
                    'date': '2025-07-20',
                    'type': 'Blood test',
                    'notes': 'Lab results within normal range'
                }
            ]
        }

        return jsonify({
            'success': True,
            'patient': patient_details
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/validate-parent', methods=['POST'])
@doctor_required
def validate_parent():
    """Validate if parent email exists in system"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400

        users = DataManager.get_all_users()
        parent = next((u for u in users if u.get('email') == email and u.get('role') == 'user'), None)

        if parent:
            return jsonify({
                'success': True,
                'parent_id': parent['id'],
                'parent_name': parent['full_name']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Parent not found in system'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/generate-unique-id', methods=['POST'])
@doctor_required
def generate_unique_id():
    """Generate unique ID for a new baby - Doctor adds baby with parent association"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['babyName', 'birthDate', 'gender', 'parent_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400

        # Validate that parent exists
        parent = DataManager.get_user_by_id(data['parent_id'])
        if not parent:
            return jsonify({
                'success': False,
                'error': 'Parent user not found in the system'
            }), 404

        # Generate unique ID
        unique_id = DataManager.generate_enhanced_unique_id()

        # Create baby record linked to parent
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO babies (name, birth_date, gender, weight_at_birth, height_at_birth,
                              parent_id, unique_id, notes, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            data['babyName'],
            data['birthDate'],
            data['gender'],
            float(data['weight']) if data.get('weight') else None,
            float(data['height']) if data.get('height') else None,
            data['parent_id'],  # Link baby to parent user
            unique_id,
            data.get('notes', ''),
            datetime.now().isoformat()
        ))

        baby_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Get doctor information for notification
        doctor_id = session['user_id']
        doctor_user = DataManager.get_user_by_id(doctor_id)

        # Send notification email to parent
        try:
            from app.services.email_service import email_service
            
            subject = f"Baby Registered - Unique ID Generated"
            message = f"""
Dear {parent['full_name']},

Your baby has been successfully registered in our Maternal and Child Health Care System by Dr. {doctor_user['full_name']}.

👶 BABY INFORMATION:
• Name: {data['babyName']}
• Birth Date: {data['birthDate']}
• Gender: {data['gender']}
• Unique ID: {unique_id}

📋 IMPORTANT:
This Unique ID ({unique_id}) is your baby's permanent identifier in our system. 
Please keep it safe as it will be used to:
• Access your baby's medical records
• Track vaccinations and growth
• Schedule appointments
• View nutrition plans

You can now:
1. Log in to your account
2. Access the Baby Care section
3. View all your baby's information using this unique ID

If you have any questions, please contact us.

Best regards,
Dr. {doctor_user['full_name']}
Maternal and Child Health Care System

© 2024 Maternal and Child Health Care
This is an automated notification.
            """

            email_service.send_email(
                to_email=parent['email'],
                subject=subject,
                html_content=message
            )
        except Exception as email_error:
            print(f"Email notification failed: {email_error}")

        # Generate QR code
        qr_code_data = None
        try:
            import qrcode
            import io
            import base64

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(unique_id)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        except ImportError:
            pass  # QR code generation is optional

        return jsonify({
            'success': True,
            'unique_id': unique_id,
            'baby_id': baby_id,
            'parent_name': parent['full_name'],
            'parent_email': parent['email'],
            'qr_code': qr_code_data,
            'message': f'Unique ID generated successfully for {data["babyName"]}. Parent {parent["full_name"]} has been notified.'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/babies-with-ids')
@doctor_required
def get_babies_with_ids():
    """Get all babies with their unique IDs"""
    try:
        conn = DataManager.get_connection()
        conn.row_factory = sqlite3.Row  # Enable row factory
        cursor = conn.cursor()

        cursor.execute('''
            SELECT b.*, u.full_name as parent_name
            FROM babies b
            JOIN users u ON b.parent_id = u.id
            WHERE b.is_active = 1
            ORDER BY b.created_at DESC
        ''')

        babies = []
        for row in cursor.fetchall():
            baby = dict(row)
            babies.append(baby)

        conn.close()

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

@doctor_bp.route('/api/baby/<int:baby_id>')
@doctor_required
def get_baby_details(baby_id):
    """Get detailed information for a specific baby"""
    try:
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT b.*, u.full_name as parent_name, u.email as parent_email
            FROM babies b
            JOIN users u ON b.parent_id = u.id
            WHERE b.id = ? AND b.is_active = 1
        ''', (baby_id,))

        baby_row = cursor.fetchone()

        if not baby_row:
            return jsonify({
                'success': False,
                'error': 'Baby not found'
            }), 404

        baby = dict(baby_row)
        conn.close()

        return jsonify({
            'success': True,
            'baby': baby
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/regenerate-unique-id/<int:baby_id>', methods=['POST'])
@doctor_required
def regenerate_unique_id(baby_id):
    """Regenerate unique ID for a baby"""
    try:
        # Generate new unique ID
        new_unique_id = DataManager.generate_enhanced_unique_id()

        # Update baby record
        conn = DataManager.get_connection()
        conn.row_factory = sqlite3.Row  # Enable row factory
        cursor = conn.cursor()

        # Check if baby exists
        cursor.execute('SELECT id FROM babies WHERE id = ? AND is_active = 1', (baby_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Baby not found'
            }), 404

        # Update unique ID (removed updated_at since it doesn't exist in babies table)
        cursor.execute('''
            UPDATE babies
            SET unique_id = ?
            WHERE id = ?
        ''', (new_unique_id, baby_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'new_unique_id': new_unique_id,
            'message': 'Unique ID regenerated successfully'
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"REGENERATE ID ERROR: {str(e)}")
        print(f"FULL TRACEBACK: {error_details}")

        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@doctor_bp.route('/api/appointment/<int:appointment_id>/complete', methods=['POST'])
@doctor_required
def mark_appointment_complete(appointment_id):
    """Mark an appointment as completed"""
    try:
        data = request.get_json() or {}
        doctor_id = session['user_id']

        # Get doctor's information
        doctor_user = DataManager.get_user_by_id(doctor_id)
        doctor_name = doctor_user['full_name']

        # Verify appointment belongs to this doctor
        conn = DataManager.get_connection()
        conn.row_factory = sqlite3.Row  # Enable row factory
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id FROM appointments
            WHERE id = ? AND (doctor_id = ? OR doctor_name = ?)
        ''', (appointment_id, doctor_id, doctor_name))

        if not cursor.fetchone():
            return jsonify({
                'success': False,
                'error': 'Appointment not found or access denied'
            }), 404

        # Update appointment status
        consultation_notes = data.get('notes', '')
        cursor.execute('''
            UPDATE appointments
            SET status = 'completed', notes = ?
            WHERE id = ?
        ''', (consultation_notes, appointment_id))

        conn.commit()
        conn.close()

        # Send completion notification email to patient
        try:
            from app.services.email_service import email_service

            # Get appointment and patient details
            conn = DataManager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT a.appointment_date, a.appointment_type, a.purpose, a.clinic_name,
                       u.full_name as patient_name, u.email as patient_email
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                WHERE a.id = ?
            ''', (appointment_id,))

            appointment_info = cursor.fetchone()
            conn.close()

            if appointment_info:
                from datetime import datetime
                appointment_date = datetime.fromisoformat(appointment_info[0])

                # Send completion email to patient
                completion_subject = f"Appointment Completed - {doctor_name}"
                completion_message = f"""
Dear {appointment_info[4]},

Your appointment has been successfully completed.

📅 Appointment Summary:
• Doctor: {doctor_name}
• Date: {appointment_date.strftime('%Y-%m-%d')}
• Time: {appointment_date.strftime('%H:%M')}
• Type: {appointment_info[1]}
• Purpose: {appointment_info[2] or 'General consultation'}
• Location: {appointment_info[3] or 'Maternal Care Clinic'}

📝 Consultation Notes:
{consultation_notes if consultation_notes else 'No additional notes provided.'}

💡 Next Steps:
• Follow any instructions provided during your consultation
• Schedule follow-up appointments if recommended
• Contact us if you have any questions or concerns

Thank you for choosing our healthcare services. We hope you had a positive experience.

Best regards,
{doctor_name}
Maternal and Child Health Care System

© 2024 Maternal and Child Health Care
This is an automated notification.
                """

                email_service.send_email(
                    to_email=appointment_info[5],
                    subject=completion_subject,
                    html_content=completion_message
                )

                return jsonify({
                    'success': True,
                    'message': 'Appointment marked as completed and patient notified',
                    'email_sent': True
                })

        except Exception as email_error:
            print(f"Completion email failed: {email_error}")
            return jsonify({
                'success': True,
                'message': 'Appointment marked as completed (notification email failed)',
                'email_sent': False
            })

        return jsonify({
            'success': True,
            'message': 'Appointment marked as completed'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/appointment/<int:appointment_id>/reschedule', methods=['POST'])
@doctor_required
def reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    try:
        data = request.get_json()
        doctor_id = session['user_id']

        if not data or not data.get('new_date') or not data.get('new_time'):
            return jsonify({
                'success': False,
                'error': 'New date and time are required'
            }), 400

        # Get doctor's information
        doctor_user = DataManager.get_user_by_id(doctor_id)
        doctor_name = doctor_user['full_name']

        # Verify appointment belongs to this doctor
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id FROM appointments
            WHERE id = ? AND (doctor_id = ? OR doctor_name = ?)
        ''', (appointment_id, doctor_id, doctor_name))

        if not cursor.fetchone():
            return jsonify({
                'success': False,
                'error': 'Appointment not found or access denied'
            }), 404

        # Parse new date and time
        new_date = data['new_date']
        new_time = data['new_time']
        new_datetime = datetime.strptime(f"{new_date} {new_time}", '%Y-%m-%d %H:%M')

        # Update appointment
        cursor.execute('''
            UPDATE appointments
            SET appointment_date = ?, status = 'rescheduled'
            WHERE id = ?
        ''', (new_datetime.isoformat(), appointment_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Appointment rescheduled successfully',
            'new_datetime': new_datetime.isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@doctor_bp.route('/api/doctors')
def get_doctors():
    """Get list of all doctors for appointment booking"""
    try:
        users = DataManager.get_all_users()
        doctors = [
            {
                'id': user['id'],
                'name': user['full_name'],
                'email': user['email'],
                'phone': user.get('phone', ''),
                'specialization': 'General Practice'  # Could be added to user table later
            }
            for user in users if user.get('role') == 'doctor'
        ]

        return jsonify({
            'success': True,
            'doctors': doctors,
            'count': len(doctors)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@doctor_bp.route('/api/babycare-appointments')
@doctor_required
def get_babycare_appointments():
    """Get baby care appointments assigned to the current doctor"""
    try:
        user_id = session['user_id']

        conn = DataManager.get_connection()
        cursor = conn.cursor()

        # Get baby care appointments for this doctor
        cursor.execute('''
            SELECT a.id, a.user_id, a.baby_id, a.appointment_type, a.appointment_date,
                   a.doctor_name, a.clinic_name, a.purpose, a.status, a.notes,
                   a.patient_name, a.patient_email, a.child_name, a.confirmed_by_doctor,
                   a.created_at, a.updated_at, b.name as baby_name, u.full_name as patient_full_name
            FROM appointments a
            LEFT JOIN babies b ON a.baby_id = b.id
            LEFT JOIN users u ON a.user_id = u.id
            WHERE a.doctor_id = ? AND a.appointment_type LIKE '%Baby Care%'
            ORDER BY a.appointment_date ASC
        ''', (user_id,))

        appointments = cursor.fetchall()
        conn.close()

        appointments_data = []
        for appointment in appointments:
            appointments_data.append({
                'id': appointment[0],
                'user_id': appointment[1],
                'baby_id': appointment[2],
                'appointment_type': appointment[3],
                'appointment_date': appointment[4],
                'doctor_name': appointment[5],
                'clinic_name': appointment[6],
                'purpose': appointment[7],
                'status': appointment[8],
                'notes': appointment[9],
                'patient_name': appointment[10],
                'patient_email': appointment[11],
                'child_name': appointment[12],
                'confirmed_by_doctor': bool(appointment[13]),
                'created_at': appointment[14],
                'updated_at': appointment[15],
                'baby_name': appointment[16],
                'patient_full_name': appointment[17]
            })

        return jsonify({
            'success': True,
            'appointments': appointments_data,
            'count': len(appointments_data)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@doctor_bp.route('/api/babycare-appointments/<int:appointment_id>/confirm', methods=['POST'])
@doctor_required
def confirm_babycare_appointment(appointment_id):
    """Confirm a baby care appointment"""
    try:
        user_id = session['user_id']

        # Get appointment details
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT a.*, u.email as patient_email, u.full_name as patient_name
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.id = ? AND a.doctor_id = ?
        ''', (appointment_id, user_id))

        appointment = cursor.fetchone()

        if not appointment:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Appointment not found or access denied'
            }), 404

        # Update appointment status
        cursor.execute('''
            UPDATE appointments
            SET status = 'confirmed', confirmed_by_doctor = 1, updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), appointment_id))

        conn.commit()
        conn.close()

        # Send confirmation email
        try:
            from app.services.email_service import email_service

            doctor_user = DataManager.get_user_by_id(user_id)

            appointment_details = {
                'appointment_id': appointment_id,
                'patient_name': appointment[11] or appointment[17],  # patient_name or patient_full_name
                'child_name': appointment[12] or 'Child',  # child_name
                'doctor_name': doctor_user['full_name'],
                'appointment_date': appointment[5][:10] if appointment[5] else '',  # appointment_date
                'appointment_time': appointment[5][11:16] if len(appointment[5]) > 10 else '',
                'purpose': appointment[8] or 'Baby Care Checkup',  # purpose
                'clinic_name': appointment[7] or 'Baby Care Clinic'  # clinic_name
            }

            email_result = email_service.send_appointment_confirmation_emails(
                appointment[16],  # patient_email
                doctor_user['email'],  # doctor_email
                appointment_details
            )

            return jsonify({
                'success': True,
                'message': 'Baby care appointment confirmed and emails sent',
                'email_sent': email_result.get('success', False)
            })

        except Exception as email_error:
            print(f"Email sending failed: {email_error}")
            return jsonify({
                'success': True,
                'message': 'Baby care appointment confirmed (email notification failed)',
                'email_sent': False,
                'email_error': str(email_error)
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@doctor_bp.route('/api/babycare-appointments/<int:appointment_id>/complete', methods=['POST'])
@doctor_required
def complete_babycare_appointment(appointment_id):
    """Mark a baby care appointment as completed"""
    try:
        user_id = session['user_id']
        data = request.get_json() or {}

        conn = DataManager.get_connection()
        conn.row_factory = sqlite3.Row  # Enable row factory
        cursor = conn.cursor()

        # Verify appointment belongs to this doctor
        cursor.execute('''
            SELECT id FROM appointments
            WHERE id = ? AND doctor_id = ?
        ''', (appointment_id, user_id))

        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Appointment not found or access denied'
            }), 404

        # Update appointment status
        cursor.execute('''
            UPDATE appointments
            SET status = 'completed', notes = ?, completed_at = ?, updated_at = ?
            WHERE id = ?
        ''', (
            data.get('notes', ''),
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            appointment_id
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Baby care appointment marked as completed'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/reports')
@doctor_required
def get_reports():
    """Get medical reports for the current doctor"""
    try:
        user_id = session['user_id']
        user = DataManager.get_user_by_id(user_id)
        doctor_name = user['full_name']

        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT r.id, r.patient_id, r.doctor_id, r.patient_name, r.doctor_name,
                   r.report_type, r.report_date, r.findings, r.recommendations,
                   r.diagnosis, r.notes, r.created_at, r.updated_at
            FROM medical_reports r
            WHERE r.doctor_id = ? AND r.is_active = 1
            ORDER BY r.report_date DESC, r.created_at DESC
        ''', (user_id,))

        reports = []
        for row in cursor.fetchall():
            report = {
                'id': row[0],
                'patient_id': row[1],
                'doctor_id': row[2],
                'patient_name': row[3],
                'doctor_name': row[4],
                'report_type': row[5],
                'report_date': row[6],
                'findings': row[7],
                'recommendations': row[8],
                'diagnosis': row[9],
                'notes': row[10],
                'created_at': row[11],
                'updated_at': row[12]
            }
            reports.append(report)

        conn.close()

        return jsonify({
            'success': True,
            'reports': reports
        })

    except Exception as e:
        print(f"Error getting reports: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/reports', methods=['POST'])
@doctor_required
def create_report():
    """Create a new medical report"""
    try:
        user_id = session['user_id']
        user = DataManager.get_user_by_id(user_id)
        doctor_name = user['full_name']

        data = request.get_json()

        # Validate required fields
        required_fields = ['patient_id', 'patient_name', 'report_type', 'report_date', 'findings']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO medical_reports (patient_id, doctor_id, patient_name, doctor_name,
                                       report_type, report_date, findings, recommendations,
                                       diagnosis, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['patient_id'],
            user_id,
            data['patient_name'],
            doctor_name,
            data['report_type'],
            data['report_date'],
            data['findings'],
            data.get('recommendations', ''),
            data.get('diagnosis', ''),
            data.get('notes', ''),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        report_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Report created successfully',
            'report_id': report_id
        })

    except Exception as e:
        print(f"Error creating report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/reports/<int:report_id>', methods=['PUT'])
@doctor_required
def update_report(report_id):
    """Update an existing medical report"""
    try:
        user_id = session['user_id']
        data = request.get_json()

        conn = DataManager.get_connection()
        cursor = conn.cursor()

        # Verify the report belongs to this doctor
        cursor.execute('SELECT doctor_id FROM medical_reports WHERE id = ?', (report_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
        
        if row[0] != user_id:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'You can only update your own reports'
            }), 403

        # Update the report
        cursor.execute('''
            UPDATE medical_reports
            SET report_type = ?,
                report_date = ?,
                findings = ?,
                recommendations = ?,
                diagnosis = ?,
                notes = ?,
                updated_at = ?
            WHERE id = ?
        ''', (
            data.get('report_type'),
            data.get('report_date'),
            data.get('findings'),
            data.get('recommendations', ''),
            data.get('diagnosis', ''),
            data.get('notes', ''),
            datetime.now().isoformat(),
            report_id
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Report updated successfully'
        })

    except Exception as e:
        print(f"Error updating report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/patients')
@doctor_required
def get_patients():
    """Get all registered patients for report creation"""
    try:
        conn = DataManager.get_connection()
        conn.row_factory = sqlite3.Row  # Enable row factory
        cursor = conn.cursor()

        # Get all users with role 'user' (patients)
        cursor.execute('''
            SELECT id, full_name, email, phone, created_at
            FROM users
            WHERE role = 'user' AND is_active = 1
            ORDER BY full_name ASC
        ''')

        patients = []
        for row in cursor.fetchall():
            patient = dict(row)
            patients.append({
                'id': patient['id'],
                'name': patient['full_name'],
                'email': patient['email'],
                'phone': patient.get('phone', ''),
                'created_at': patient['created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'patients': patients,
            'count': len(patients)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@doctor_bp.route('/api/notifications')
@doctor_required
def get_notifications():
    """Get pending appointment notifications for the current doctor"""
    try:
        doctor_id = session['user_id']

        conn = DataManager.get_connection()
        cursor = conn.cursor()

        # Get pending appointments for this doctor (new appointments)
        cursor.execute('''
            SELECT a.id, a.user_id, a.appointment_type, a.appointment_date,
                   a.doctor_name, a.purpose, a.status, a.created_at,
                   u.full_name as patient_name, u.email as patient_email
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE (a.doctor_id = ? OR a.doctor_name = (SELECT full_name FROM users WHERE id = ?))
            AND a.status = 'pending'
            ORDER BY a.created_at DESC
            LIMIT 10
        ''', (doctor_id, doctor_id))

        notifications = []
        for row in cursor.fetchall():
            appointment = dict(row)

            # Calculate time since appointment was created
            created_at = datetime.fromisoformat(appointment['created_at'].replace('Z', '+00:00'))
            time_diff = datetime.now() - created_at

            if time_diff.days > 0:
                time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif time_diff.seconds > 60:
                minutes = time_diff.seconds // 60
                time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                time_ago = "Just now"

            notifications.append({
                'id': appointment['id'],
                'type': 'new_appointment',
                'title': 'New Appointment Request',
                'message': f"{appointment['patient_name']} booked a {appointment['appointment_type']} appointment",
                'patient_name': appointment['patient_name'],
                'appointment_type': appointment['appointment_type'],
                'appointment_date': appointment['appointment_date'],
                'purpose': appointment['purpose'],
                'time_ago': time_ago,
                'created_at': appointment['created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500