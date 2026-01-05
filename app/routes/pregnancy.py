from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file, current_app
from datetime import datetime, date, timedelta
from app.data_manager import DataManager
import uuid
import json
import csv
import io
import sqlite3
from xhtml2pdf import pisa

pregnancy_bp = Blueprint('pregnancy', __name__, url_prefix='/pregnancy')

def login_required(f):
    """Simple login required decorator"""
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Page Routes

@pregnancy_bp.route('/')
@login_required
def index():
    """Pregnancy care main page"""
    return render_template('pregnancy/pregnancy.html')

@pregnancy_bp.route('/nutrition')
@login_required
def nutrition():
    """Pregnancy nutrition page"""
    return render_template('pregnancy/nutrition.html')

@pregnancy_bp.route('/exercise')
@login_required
def exercise():
    """Pregnancy exercise page"""
    return render_template('pregnancy/exercise.html')

@pregnancy_bp.route('/meditation')
@login_required
def meditation():
    """Pregnancy meditation page"""
    return render_template('pregnancy/meditation.html')

@pregnancy_bp.route('/weight-tracker')
@login_required
def weight_tracker():
    """Pregnancy weight tracker page"""
    return render_template('pregnancy/weight_tracker.html')

@pregnancy_bp.route('/appointments')
@login_required
def appointments():
    """Pregnancy appointments page"""
    return render_template('pregnancy/appointments.html')

@pregnancy_bp.route('/faq')
@login_required
def faq():
    """Pregnancy FAQ page"""
    return render_template('pregnancy/faq.html')

@pregnancy_bp.route('/schemes')
@login_required
def schemes():
    """Pregnancy schemes page"""
    return render_template('pregnancy/schemes.html')

@pregnancy_bp.route('/reports')
@login_required
def reports():
    """Pregnancy reports page"""
    return render_template('pregnancy/reports.html')

@pregnancy_bp.route('/assistant')
@login_required
def assistant():
    """Pregnancy assistant page"""
    return render_template('pregnancy/assistant.html')

# API Routes

# Removed old nutrition API - now using admin-managed content from /api/nutrition-data

# Weight Tracker API Routes

def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (cm)"""
    if height and weight:
        height_m = height / 100  # Convert cm to meters
        return round(weight / (height_m ** 2), 1)
    return None

def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi is None:
        return 'unknown'
    if bmi < 18.5:
        return 'underweight'
    elif bmi < 25:
        return 'normal'
    elif bmi < 30:
        return 'overweight'
    else:
        return 'obese'

def get_recommended_gain_range(bmi_category):
    """Get recommended weight gain range based on BMI category"""
    ranges = {
        'underweight': {'total': '12.7-18.1 kg', 'weekly': '0.5 kg/week (2nd & 3rd trimester)'},
        'normal': {'total': '11.3-15.9 kg', 'weekly': '0.4 kg/week (2nd & 3rd trimester)'},
        'overweight': {'total': '6.8-11.3 kg', 'weekly': '0.3 kg/week (2nd & 3rd trimester)'},
        'obese': {'total': '5.0-9.1 kg', 'weekly': '0.2 kg/week (2nd & 3rd trimester)'}
    }
    return ranges.get(bmi_category, {'total': 'Consult your doctor', 'weekly': 'Consult your doctor'})

def get_status(bmi_category, weight_gain, pregnancy_week):
    """Determine if weight gain is on track"""
    if not weight_gain or not pregnancy_week:
        return 'unknown'
    
    # Rough guidelines for weekly gain in 2nd and 3rd trimester
    weekly_ranges = {
        'underweight': (0.45, 0.55),
        'normal': (0.35, 0.45),
        'overweight': (0.25, 0.35),
        'obese': (0.15, 0.25)
    }
    
    if pregnancy_week < 13:
        # First trimester - minimal gain expected
        if weight_gain > 3:
            return 'high'
        return 'good'
    
    # Calculate expected weeks of weight gain (subtract first trimester)
    weeks_of_gain = pregnancy_week - 13
    
    if bmi_category in weekly_ranges:
        low, high = weekly_ranges[bmi_category]
        expected_low = weeks_of_gain * low
        expected_high = weeks_of_gain * high
        
        if weight_gain < expected_low * 0.7:  # More than 30% below
            return 'low'
        elif weight_gain > expected_high * 1.3:  # More than 30% above
            return 'high'
    
    return 'good'

@pregnancy_bp.route('/api/weight-entries', methods=['GET'])
@login_required
def get_weight_entries():
    """Get all weight entries for the current user"""
    try:
        user_id = session.get('user_id')
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, date, weight, pregnancy_week, 
                   pre_pregnancy_weight, height, bmi, weight_gain, notes, created_at
            FROM weight_entries
            WHERE user_id = ?
            ORDER BY pregnancy_week DESC, date DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        entries = []
        for row in rows:
            bmi = row[7]
            bmi_category = get_bmi_category(bmi)
            recommended_gain = get_recommended_gain_range(bmi_category)
            status = get_status(bmi_category, row[8], row[4])
            
            entries.append({
                'id': row[0],
                'user_id': row[1],
                'date': row[2],
                'weight': row[3],
                'pregnancy_week': row[4],
                'pre_pregnancy_weight': row[5],
                'height': row[6],
                'bmi': bmi,
                'bmi_category': bmi_category,
                'weight_gain': row[8],
                'status': status,
                'recommended_gain': recommended_gain,
                'notes': row[9],
                'created_at': row[10]
            })
        
        return jsonify({
            'success': True,
            'entries': entries
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pregnancy_bp.route('/api/weight-entries', methods=['POST'])
@login_required
def add_weight_entry():
    """Add a new weight entry"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()

        # Validate required fields
        required_fields = ['weight', 'pregnancy_week']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Extract data
        weight = float(data['weight'])
        pregnancy_week = int(data['pregnancy_week'])
        pre_pregnancy_weight = float(data.get('pre_pregnancy_weight')) if data.get('pre_pregnancy_weight') else None
        height = float(data.get('height')) if data.get('height') else None
        notes = data.get('notes', '')
        
        # Calculate BMI and weight gain
        bmi = calculate_bmi(weight, height) if height else None
        weight_gain = round(weight - pre_pregnancy_weight, 1) if pre_pregnancy_weight else None
        
        # Insert into database
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO weight_entries 
            (user_id, weight, pregnancy_week, pre_pregnancy_weight, height, bmi, weight_gain, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, weight, pregnancy_week, pre_pregnancy_weight, height, bmi, weight_gain, notes))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        # Get the inserted entry
        cursor.execute('''
            SELECT id, user_id, date, weight, pregnancy_week, 
                   pre_pregnancy_weight, height, bmi, weight_gain, notes, created_at
            FROM weight_entries WHERE id = ?
        ''', (entry_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        # Build response
        bmi_category = get_bmi_category(bmi)
        recommended_gain = get_recommended_gain_range(bmi_category)
        status = get_status(bmi_category, weight_gain, pregnancy_week)
        
        entry = {
            'id': row[0],
            'user_id': row[1],
            'date': row[2],
            'weight': row[3],
            'pregnancy_week': row[4],
            'pre_pregnancy_weight': row[5],
            'height': row[6],
            'bmi': bmi,
            'bmi_category': bmi_category,
            'weight_gain': row[8],
            'status': status,
            'recommended_gain': recommended_gain,
            'notes': row[9],
            'created_at': row[10]
        }

        return jsonify({
            'success': True,
            'message': 'Weight entry added successfully',
            'entry': entry
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid data format'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pregnancy_bp.route('/api/weight-entries/<int:entry_id>', methods=['PUT'])
@login_required
def update_weight_entry(entry_id):
    """Update an existing weight entry"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()

        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()
        
        # Check if entry exists and belongs to user
        cursor.execute('SELECT * FROM weight_entries WHERE id = ? AND user_id = ?', (entry_id, user_id))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Weight entry not found'
            }), 404

        # Build update query dynamically
        update_fields = []
        update_values = []
        
        if 'weight' in data:
            update_fields.append('weight = ?')
            update_values.append(float(data['weight']))
        if 'pregnancy_week' in data:
            update_fields.append('pregnancy_week = ?')
            update_values.append(int(data['pregnancy_week']))
        if 'pre_pregnancy_weight' in data:
            update_fields.append('pre_pregnancy_weight = ?')
            update_values.append(float(data['pre_pregnancy_weight']) if data['pre_pregnancy_weight'] else None)
        if 'height' in data:
            update_fields.append('height = ?')
            update_values.append(float(data['height']) if data['height'] else None)
        if 'notes' in data:
            update_fields.append('notes = ?')
            update_values.append(data['notes'])
        
        # Get current data for recalculation
        cursor.execute('SELECT weight, pre_pregnancy_weight, height FROM weight_entries WHERE id = ?', (entry_id,))
        current = cursor.fetchone()
        
        weight = float(data.get('weight', current[0]))
        pre_pregnancy_weight = float(data.get('pre_pregnancy_weight', current[1])) if data.get('pre_pregnancy_weight', current[1]) else None
        height = float(data.get('height', current[2])) if data.get('height', current[2]) else None
        
        # Recalculate
        bmi = calculate_bmi(weight, height) if height else None
        weight_gain = round(weight - pre_pregnancy_weight, 1) if pre_pregnancy_weight else None
        
        update_fields.extend(['bmi = ?', 'weight_gain = ?'])
        update_values.extend([bmi, weight_gain])
        
        # Add entry_id and user_id for WHERE clause
        update_values.extend([entry_id, user_id])
        
        cursor.execute(f'''
            UPDATE weight_entries 
            SET {', '.join(update_fields)}
            WHERE id = ? AND user_id = ?
        ''', update_values)
        
        conn.commit()
        
        # Get updated entry
        cursor.execute('''
            SELECT id, user_id, date, weight, pregnancy_week, 
                   pre_pregnancy_weight, height, bmi, weight_gain, notes, created_at
            FROM weight_entries WHERE id = ?
        ''', (entry_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        bmi_category = get_bmi_category(bmi)
        recommended_gain = get_recommended_gain_range(bmi_category)
        status = get_status(bmi_category, weight_gain, row[4])
        
        entry = {
            'id': row[0],
            'user_id': row[1],
            'date': row[2],
            'weight': row[3],
            'pregnancy_week': row[4],
            'pre_pregnancy_weight': row[5],
            'height': row[6],
            'bmi': bmi,
            'bmi_category': bmi_category,
            'weight_gain': row[8],
            'status': status,
            'recommended_gain': recommended_gain,
            'notes': row[9],
            'created_at': row[10]
        }

        return jsonify({
            'success': True,
            'message': 'Weight entry updated successfully',
            'entry': entry
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid data format'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pregnancy_bp.route('/api/weight-entries/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_weight_entry(entry_id):
    """Delete a weight entry"""
    try:
        user_id = session.get('user_id')
        
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM weight_entries WHERE id = ? AND user_id = ?', (entry_id, user_id))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Weight entry deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Weight entry not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pregnancy_bp.route('/api/weight-entries/latest', methods=['GET'])
@login_required
def get_latest_weight_entry():
    """Get the latest weight entry for the current user"""
    try:
        user_id = session.get('user_id')
        
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, date, weight, pregnancy_week, 
                   pre_pregnancy_weight, height, bmi, weight_gain, notes, created_at
            FROM weight_entries
            WHERE user_id = ?
            ORDER BY pregnancy_week DESC, date DESC
            LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            bmi = row[7]
            bmi_category = get_bmi_category(bmi)
            recommended_gain = get_recommended_gain_range(bmi_category)
            status = get_status(bmi_category, row[8], row[4])
            
            entry = {
                'id': row[0],
                'user_id': row[1],
                'date': row[2],
                'weight': row[3],
                'pregnancy_week': row[4],
                'pre_pregnancy_weight': row[5],
                'height': row[6],
                'bmi': bmi,
                'bmi_category': bmi_category,
                'weight_gain': row[8],
                'status': status,
                'recommended_gain': recommended_gain,
                'notes': row[9],
                'created_at': row[10]
            }
            
            return jsonify({
                'success': True,
                'entry': entry
            })
        else:
            return jsonify({
                'success': True,
                'entry': None
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pregnancy_bp.route('/api/weight-entries/export-csv', methods=['GET'])
@login_required
def export_weight_entries_csv():
    """Export weight entries as CSV"""
    try:
        user_id = session.get('user_id')
        
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, pregnancy_week, weight, pre_pregnancy_weight, 
                   height, bmi, weight_gain, notes
            FROM weight_entries
            WHERE user_id = ?
            ORDER BY pregnancy_week ASC, date ASC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Pregnancy Week', 'Weight (kg)', 'Pre-pregnancy Weight (kg)', 
                        'Height (cm)', 'BMI', 'Weight Gain (kg)', 'Status', 'Notes'])
        
        # Write data
        for row in rows:
            bmi_category = get_bmi_category(row[5])
            status = get_status(bmi_category, row[6], row[1])
            
            writer.writerow([
                row[0] if row[0] else '',
                row[1],
                row[2],
                row[3] or '',
                row[4] or '',
                row[5] or '',
                row[6] or '',
                status,
                row[7] or ''
            ])
        
        # Prepare response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'weight_tracker_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Medical Reports API Routes

@pregnancy_bp.route('/api/medical-reports')
@login_required
def get_medical_reports():
    """Get all medical reports for the current user"""
    try:
        user_id = session['user_id']
        
        conn = DataManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, doctor_id, doctor_name, report_type, report_date,
                   findings, recommendations, diagnosis, notes,
                   created_at, updated_at
            FROM medical_reports
            WHERE patient_id = ? AND is_active = 1
            ORDER BY report_date DESC, created_at DESC
        ''', (user_id,))
        
        reports = []
        for row in cursor.fetchall():
            report = {
                'id': row[0],
                'doctor_id': row[1],
                'doctor_name': row[2],
                'report_type': row[3],
                'report_date': row[4],
                'findings': row[5],
                'recommendations': row[6],
                'diagnosis': row[7],
                'notes': row[8],
                'created_at': row[9],
                'updated_at': row[10]
            }
            reports.append(report)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'reports': reports,
            'count': len(reports)
        })
        
    except Exception as e:
        print(f"Error getting medical reports: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pregnancy_bp.route('/api/medical-reports/<int:report_id>')
@login_required
def get_medical_report_detail(report_id):
    """Get detailed information for a specific medical report"""
    try:
        user_id = session['user_id']
        
        conn = DataManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, patient_id, doctor_id, patient_name, doctor_name,
                   report_type, report_date, findings, recommendations,
                   diagnosis, notes, created_at, updated_at
            FROM medical_reports
            WHERE id = ? AND patient_id = ? AND is_active = 1
        ''', (report_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Report not found or access denied'
            }), 404
        
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
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        print(f"Error getting report detail: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pregnancy_bp.route('/api/medical-reports/<int:report_id>/download')
@login_required
def download_medical_report(report_id):
    """Download medical report as PDF"""
    try:
        user_id = session['user_id']
        
        conn = DataManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, patient_id, doctor_id, patient_name, doctor_name,
                   report_type, report_date, findings, recommendations,
                   diagnosis, notes, created_at, updated_at
            FROM medical_reports
            WHERE id = ? AND patient_id = ? AND is_active = 1
        ''', (report_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Report not found or access denied'
            }), 404
        
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
        
        # Generate HTML report
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Medical Report - {report['report_type']}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #f472b6;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #581c87;
                    margin: 0;
                    font-size: 28px;
                }}
                .header p {{
                    color: #666;
                    margin: 5px 0 0 0;
                }}
                .report-info {{
                    background: #fdf2f8;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .info-row {{
                    margin-bottom: 10px;
                    overflow: hidden;
                }}
                .info-label {{
                    font-weight: bold;
                    float: left;
                    width: 150px;
                    color: #581c87;
                }}
                .info-value {{
                    margin-left: 150px;
                }}
                .section {{
                    margin-bottom: 30px;
                    page-break-inside: avoid;
                }}
                .section h2 {{
                    color: #581c87;
                    border-bottom: 2px solid #f472b6;
                    padding-bottom: 10px;
                    font-size: 20px;
                    margin-top: 0;
                }}
                .section-content {{
                    padding: 15px;
                    background: #fafafa;
                    border-radius: 8px;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
                .footer {{
                    margin-top: 50px;
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    border-top: 1px solid #ddd;
                    padding-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 Medical Report</h1>
                <p>Maternal and Child Health Monitoring System</p>
            </div>
            
            <div class="report-info">
                <div class="info-row">
                    <div class="info-label">Report ID:</div>
                    <div class="info-value">{report['id']}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Patient Name:</div>
                    <div class="info-value">{report['patient_name']}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Doctor Name:</div>
                    <div class="info-value">{report['doctor_name']}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Report Type:</div>
                    <div class="info-value">{report['report_type']}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Report Date:</div>
                    <div class="info-value">{report['report_date']}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Diagnosis</h2>
                <div class="section-content">{report['diagnosis'] or 'Not specified'}</div>
            </div>
            
            <div class="section">
                <h2>Findings</h2>
                <div class="section-content">{report['findings']}</div>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <div class="section-content">{report['recommendations'] or 'No recommendations provided'}</div>
            </div>
            
            {f'<div class="section"><h2>Additional Notes</h2><div class="section-content">{report["notes"]}</div></div>' if report['notes'] else ''}
            
            <div class="footer">
                <p>Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
                <p>This is a computer-generated report from the Maternal and Child Health Monitoring System</p>
            </div>
        </body>
        </html>
        '''
        
        # Convert HTML to PDF using xhtml2pdf
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.BytesIO(html_content.encode('utf-8')), dest=pdf_buffer)
        
        if pisa_status.err:
            raise Exception("Error generating PDF")
        
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'medical_report_{report_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
        
    except Exception as e:
        print(f"Error downloading report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
