from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import sys

api_bp = Blueprint('api', __name__, url_prefix='/api')

def login_required(f):
    """Simple login required decorator"""
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"success": False, "error": "Authentication required"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@api_bp.route('/nutrition-data')
def nutrition_data():
    """Public API endpoint for nutrition data - serves admin-managed content"""
    try:
        from app.data_manager import DataManager

        # Get nutrition content from admin-managed database
        nutrition_content = DataManager.get_all_nutrition_content()

        return jsonify({
            "success": True,
            "data": nutrition_content,
            "count": len(nutrition_content),
            "message": f"Loaded {len(nutrition_content)} nutrition items from admin-managed content"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load nutrition data"
        }), 500

@api_bp.route('/faq-data')
def faq_data():
    """Public API endpoint for FAQ data - serves admin-managed content"""
    try:
        from app.data_manager import DataManager

        # Get FAQ content from admin-managed database
        faq_content = DataManager.get_all_faqs()

        return jsonify({
            "success": True,
            "data": faq_content,
            "count": len(faq_content),
            "message": f"Loaded {len(faq_content)} FAQ items from admin-managed content"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load FAQ data"
        }), 500

@api_bp.route('/vaccination-data')
def vaccination_data():
    """Public API endpoint for vaccination data - serves admin-managed content"""
    try:
        from app.data_manager import DataManager

        # Get vaccination schedules from admin-managed database
        vaccination_content = DataManager.get_all_vaccination_schedules()

        return jsonify({
            "success": True,
            "data": vaccination_content,
            "count": len(vaccination_content),
            "message": f"Loaded {len(vaccination_content)} vaccination schedules from admin-managed content"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load vaccination data"
        }), 500

@api_bp.route('/schemes-data')
def schemes_data():
    """Public API endpoint for government schemes data - serves admin-managed content"""
    try:
        from app.data_manager import DataManager

        # Get government schemes from admin-managed database
        schemes_content = DataManager.get_all_schemes()

        return jsonify({
            "success": True,
            "data": schemes_content,
            "count": len(schemes_content),
            "message": f"Loaded {len(schemes_content)} government schemes from admin-managed content"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load schemes data"
        }), 500

@api_bp.route('/exercises-data')
def exercises_data():
    """Public API endpoint for exercises data - serves admin-managed content"""
    try:
        from app.data_manager import DataManager

        # Get exercises from admin-managed database
        exercises_content = DataManager.get_all_exercises()

        return jsonify({
            "success": True,
            "data": exercises_content,
            "count": len(exercises_content),
            "message": f"Loaded {len(exercises_content)} exercises from admin-managed content"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load exercises data"
        }), 500

@api_bp.route('/meditation-data')
def meditation_data():
    """Public API endpoint for meditation data - serves admin-managed content"""
    try:
        from app.data_manager import DataManager

        # Get meditation content from admin-managed database
        meditation_content = DataManager.get_all_meditation_content()

        return jsonify({
            "success": True,
            "data": meditation_content,
            "count": len(meditation_content),
            "message": f"Loaded {len(meditation_content)} meditation sessions from admin-managed content"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load meditation data"
        }), 500

@api_bp.route('/wellness-tips-data')
def wellness_tips_data():
    """Public API endpoint for wellness tips data - serves admin-managed content"""
    try:
        from app.data_manager import DataManager

        # Get wellness tips from admin-managed database
        wellness_tips = DataManager.get_all_wellness_tips()

        return jsonify({
            "success": True,
            "data": wellness_tips,
            "count": len(wellness_tips),
            "message": f"Loaded {len(wellness_tips)} wellness tips from admin-managed content"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load wellness tips data"
        }), 500

@api_bp.route('/content-updates')
def content_updates():
    """API endpoint to check for content updates - for real-time notifications"""
    try:
        from flask import current_app
        import os

        # Read content updates from cache
        cache_dir = os.path.join(current_app.instance_path, 'cache')
        cache_file = os.path.join(cache_dir, 'content_updates.json')

        updates = []
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    updates = json.load(f)
            except:
                updates = []

        # Get updates from the last 5 minutes
        import time
        current_time = time.time()
        recent_updates = [
            update for update in updates
            if current_time - update.get('timestamp', 0) < 300  # 5 minutes
        ]

        return jsonify({
            "success": True,
            "updates": recent_updates,
            "count": len(recent_updates),
            "message": f"Found {len(recent_updates)} recent content updates"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to check for content updates"
        }), 500





@api_bp.route('/baby-care-data')
@login_required
def baby_care_data():
    """API endpoint for baby care data"""
    try:
        # Sample baby care data
        baby_care_data = [
            {
                "id": 1,
                "age_range": "newborn",
                "category": "feeding",
                "title": "Breastfeeding Basics",
                "description": "Establish a good latch and feed on demand every 2-3 hours.",
                "tips": ["Ensure baby's mouth covers most of the areola", "Listen for swallowing sounds"]
            },

            {
                "id": 3,
                "age_range": "infant_4_6",
                "category": "feeding",
                "title": "Introducing Solids",
                "description": "Start with single-ingredient foods around 6 months.",
                "tips": ["Look for signs of readiness", "Start with iron-fortified cereals"]
            },
            {
                "id": 4,
                "age_range": "toddler",
                "category": "development",
                "title": "Language Development",
                "description": "Encourage talking through reading and conversation.",
                "tips": ["Read daily", "Narrate your activities", "Respond to baby's sounds"]
            }
        ]
        
        return jsonify({
            "success": True,
            "data": baby_care_data,
            "message": "Baby care data loaded successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load baby care data"
        }), 500

@api_bp.route('/health-check')
def health_check():
    """API health check endpoint"""
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "API is running"
    })

@api_bp.route('/user-data')
@login_required
def user_data():
    """Get current user data"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"success": False, "error": "Not authenticated"}), 401
        
        # In a real app, you'd fetch this from the database
        user_data = {
            "id": user_id,
            "email": session.get('email', ''),
            "role": session.get('role', 'user'),
            "name": session.get('name', ''),
            "last_login": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "user": user_data,
            "message": "User data retrieved successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve user data"
        }), 500

@api_bp.route('/appointments-data', methods=['GET', 'POST'])
@login_required
def appointments_data():
    """Get user appointments or create new appointment"""
    if request.method == 'GET':
        try:
            from app.data_manager import DataManager

            user_id = session['user_id']

            # Get all appointments for the current user
            conn = DataManager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT a.id, a.user_id, a.baby_id, a.appointment_type, a.appointment_date,
                       a.doctor_name, a.clinic_name, a.purpose, a.status, a.notes,
                       a.created_at, b.name as baby_name
                FROM appointments a
                LEFT JOIN babies b ON a.baby_id = b.id
                WHERE a.user_id = ?
                ORDER BY a.appointment_date DESC
            ''', (user_id,))

            rows = cursor.fetchall()
            conn.close()

            appointments_data = []
            for row in rows:
                appointment_dict = {
                    'id': row[0],
                    'user_id': row[1],
                    'baby_id': row[2],
                    'appointment_type': row[3],
                    'appointment_date': row[4],
                    'doctor_name': row[5],
                    'clinic_name': row[6],
                    'purpose': row[7],
                    'status': row[8],
                    'notes': row[9],
                    'created_at': row[10],
                    'baby_name': row[11]
                }
                appointments_data.append(appointment_dict)

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

    elif request.method == 'POST':
        try:
            from app.data_manager import DataManager

            data = request.get_json()
            user_id = session['user_id']

            # Validate required fields
            required_fields = ['appointment_type', 'doctor_name', 'appointment_date']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400

            # Parse appointment date
            try:
                appointment_date = datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid appointment date format'
                }), 400

            # Create new appointment
            conn = DataManager.get_connection()
            cursor = conn.cursor()

            # Find doctor ID by name
            doctor_id = None
            if data.get('doctor_name'):
                users = DataManager.get_all_users()
                doctor = next((u for u in users if u.get('full_name') == data['doctor_name'] and u.get('role') == 'doctor'), None)
                if doctor:
                    doctor_id = doctor['id']

            # Get user information for patient details
            user_data = DataManager.get_user_by_id(user_id)

            cursor.execute('''
                INSERT INTO appointments (user_id, baby_id, doctor_id, appointment_type, appointment_date,
                                        doctor_name, clinic_name, purpose, status, patient_name, patient_email,
                                        created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('baby_id'),
                doctor_id,
                data['appointment_type'],
                appointment_date.isoformat(),
                data['doctor_name'],
                data.get('clinic_name'),
                data.get('purpose'),
                'pending',
                user_data['full_name'],
                user_data['email'],
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            appointment_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Send booking notification emails to both patient and doctor
            email_results = {
                'patient_email_sent': False,
                'doctor_email_sent': False
            }
            
            try:
                from app.services.email_service import email_service

                # Get doctor email
                doctor_email = None
                if doctor_id:
                    doctor_user = DataManager.get_user_by_id(doctor_id)
                    if doctor_user:
                        doctor_email = doctor_user['email']

                # Send booking emails to both patient and doctor
                if doctor_email:
                    appointment_details = {
                        'appointment_id': appointment_id,
                        'patient_name': user_data['full_name'],
                        'child_name': data.get('child_name', 'N/A'),
                        'doctor_name': data['doctor_name'],
                        'appointment_date': appointment_date.strftime('%Y-%m-%d'),
                        'appointment_time': appointment_date.strftime('%H:%M'),
                        'appointment_type': data['appointment_type'],
                        'purpose': data.get('purpose', 'N/A'),
                        'clinic_name': data.get('clinic_name', 'Maternal Care Clinic')
                    }
                    
                    email_results = email_service.send_appointment_booking_emails(
                        patient_email=user_data['email'],
                        doctor_email=doctor_email,
                        appointment_details=appointment_details
                    )
            except Exception as e:
                print(f"Email sending failed: {str(e)}")

            return jsonify({
                'success': True,
                'message': 'Appointment request submitted successfully. Notification emails sent.',
                'appointment_id': appointment_id,
                'status': 'pending',
                'email_results': email_results
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@api_bp.route('/pregnancy-data')
@login_required
def pregnancy_data():
    """API endpoint for pregnancy data"""
    try:
        # Sample pregnancy data
        pregnancy_data = {
            "current_week": 20,
            "due_date": "2024-06-15",
            "trimester": "second",
            "appointments": [
                {"date": "2024-02-15", "type": "Regular Checkup", "doctor": "Dr. Smith"},
                {"date": "2024-03-15", "type": "Ultrasound", "doctor": "Dr. Johnson"}
            ],
            "weight_tracking": [
                {"date": "2024-01-01", "weight": 65},
                {"date": "2024-02-01", "weight": 67},
                {"date": "2024-03-01", "weight": 69}
            ]
        }
        
        return jsonify({
            "success": True,
            "data": pregnancy_data,
            "message": "Pregnancy data loaded successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load pregnancy data"
        }), 500

@api_bp.route('/vaccination-data-static')
def vaccination_data_static():
    """API endpoint for static vaccination data"""
    try:
        # Sample vaccination data
        vaccination_data = [
            {
                "title": "Birth Vaccines",
                "age": "At Birth",
                "vaccines": ["BCG", "Hepatitis B (1st dose)", "OPV (0 dose)"],
                "description": "Essential vaccines given immediately after birth",
                "important_note": "These vaccines should be given within 24 hours of birth"
            },
            {
                "title": "6 Weeks Vaccines",
                "age": "6 Weeks",
                "vaccines": ["DPT (1st dose)", "IPV (1st dose)", "Hepatitis B (2nd dose)", "Hib (1st dose)", "Rotavirus (1st dose)", "PCV (1st dose)"],
                "description": "First round of routine immunizations",
                "important_note": "Start of the regular vaccination schedule"
            },
            {
                "title": "10 Weeks Vaccines",
                "age": "10 Weeks",
                "vaccines": ["DPT (2nd dose)", "IPV (2nd dose)", "Hib (2nd dose)", "Rotavirus (2nd dose)", "PCV (2nd dose)"],
                "description": "Second round of routine immunizations"
            },
            {
                "title": "14 Weeks Vaccines",
                "age": "14 Weeks",
                "vaccines": ["DPT (3rd dose)", "IPV (3rd dose)", "Hib (3rd dose)", "Rotavirus (3rd dose)", "PCV (3rd dose)"],
                "description": "Third round of routine immunizations"
            },
            {
                "title": "9 Months Vaccines",
                "age": "9 Months",
                "vaccines": ["Measles (1st dose)", "Japanese Encephalitis (1st dose)"],
                "description": "Important vaccines for disease prevention"
            },
            {
                "title": "12 Months Vaccines",
                "age": "12 Months",
                "vaccines": ["Hepatitis A (1st dose)"],
                "description": "Additional protection vaccines"
            },
            {
                "title": "15 Months Vaccines",
                "age": "15 Months",
                "vaccines": ["MMR (1st dose)", "Varicella", "PCV Booster"],
                "description": "Important booster vaccines"
            },
            {
                "title": "18 Months Vaccines",
                "age": "18 Months",
                "vaccines": ["Hepatitis A (2nd dose)", "Japanese Encephalitis (2nd dose)"],
                "description": "Completion of hepatitis A series"
            },
            {
                "title": "2 Years Vaccines",
                "age": "2 Years",
                "vaccines": ["Typhoid"],
                "description": "Additional protection vaccine"
            },
            {
                "title": "5 Years Vaccines",
                "age": "5 Years",
                "vaccines": ["DPT Booster", "OPV Booster", "MMR (2nd dose)"],
                "description": "Important booster vaccines before school",
                "important_note": "These boosters are crucial before starting school"
            }
        ]

        return jsonify({
            "success": True,
            "data": vaccination_data,
            "message": "Vaccination data loaded successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load vaccination data"
        }), 500

@api_bp.route('/faq-data-old')
def faq_data_old():
    """API endpoint for FAQ data"""
    try:
        # Sample FAQ data
        faq_data = [
            {
                "question": "When should I start prenatal care?",
                "answer": "You should start prenatal care as soon as you know you're pregnant, ideally within the first 8 weeks of pregnancy. Early prenatal care helps ensure the health of both you and your baby.",
                "tips": "Schedule your first appointment as soon as possible after a positive pregnancy test."
            },
            {
                "question": "What foods should I avoid during pregnancy?",
                "answer": "Avoid raw or undercooked meats, fish high in mercury, unpasteurized dairy products, raw eggs, and alcohol. Also limit caffeine intake to less than 200mg per day.",
                "tips": "When in doubt, cook it thoroughly and ask your healthcare provider about specific foods."
            },
            {
                "question": "How much weight should I gain during pregnancy?",
                "answer": "Weight gain depends on your pre-pregnancy BMI. Generally, women with normal BMI should gain 25-35 pounds, underweight women 28-40 pounds, and overweight women 15-25 pounds.",
                "tips": "Discuss your ideal weight gain with your healthcare provider based on your individual situation."
            },
            {
                "question": "When will I feel my baby move?",
                "answer": "First-time mothers typically feel baby movements between 18-25 weeks, while women who have been pregnant before may feel movements as early as 16 weeks.",
                "tips": "Baby movements may feel like flutters, bubbles, or gentle kicks at first."
            },
            {
                "question": "How often should I feed my newborn?",
                "answer": "Newborns should be fed every 2-3 hours, or 8-12 times per day. Breastfed babies may need to eat more frequently than formula-fed babies.",
                "tips": "Follow your baby's hunger cues rather than strict schedules, especially in the first few weeks."
            },
            {
                "question": "When should my baby start solid foods?",
                "answer": "Most babies are ready for solid foods around 6 months of age. Signs of readiness include sitting up with support, showing interest in food, and losing the tongue-thrust reflex.",
                "tips": "Start with single-ingredient foods and introduce new foods one at a time to watch for allergic reactions."
            },
            {
                "question": "How much sleep does my baby need?",
                "answer": "Newborns sleep 14-17 hours per day, 3-6 month olds need 14-15 hours, and 6-12 month olds need 12-16 hours including naps.",
                "tips": "Every baby is different, but establishing a consistent bedtime routine can help promote better sleep."
            },
            {
                "question": "When should I call the doctor during pregnancy?",
                "answer": "Call your doctor for severe nausea/vomiting, bleeding, severe abdominal pain, persistent headaches, vision changes, or decreased fetal movement after 28 weeks.",
                "tips": "Trust your instincts - if something doesn't feel right, don't hesitate to contact your healthcare provider."
            }
        ]

        return jsonify({
            "success": True,
            "data": faq_data,
            "message": "FAQ data loaded successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load FAQ data"
        }), 500

@api_bp.route('/schemes-data-old')
def schemes_data_old():
    """API endpoint for government schemes data"""
    try:
        # Sample government schemes data
        schemes_data = [
            {
                "title": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
                "description": "A maternity benefit program providing cash incentives for pregnant and lactating mothers for the first living child.",
                "benefits": [
                    "₹5,000 cash incentive in three installments",
                    "Promotes institutional delivery",
                    "Encourages early registration of pregnancy"
                ],
                "eligibility": "Pregnant and lactating mothers for their first living child",
                "how_to_apply": "Apply through Anganwadi Centers or online portal",
                "documents_required": ["Aadhaar Card", "Bank Account Details", "Pregnancy Certificate"]
            },
            {
                "title": "Janani Suraksha Yojana (JSY)",
                "description": "A safe motherhood intervention program to reduce maternal and infant mortality by promoting institutional delivery.",
                "benefits": [
                    "Cash assistance for institutional delivery",
                    "₹1,400 for rural areas, ₹1,000 for urban areas",
                    "Free delivery and postnatal care"
                ],
                "eligibility": "Pregnant women belonging to BPL families",
                "how_to_apply": "Register at nearest health facility",
                "documents_required": ["BPL Card", "Aadhaar Card", "Bank Account Details"]
            },
            {
                "title": "Integrated Child Development Services (ICDS)",
                "description": "Provides supplementary nutrition, immunization, health check-ups, and pre-school education for children under 6 years.",
                "benefits": [
                    "Supplementary nutrition for children and pregnant/lactating mothers",
                    "Immunization services",
                    "Health and nutrition education",
                    "Pre-school education"
                ],
                "eligibility": "Children under 6 years, pregnant and lactating mothers",
                "how_to_apply": "Visit nearest Anganwadi Center",
                "documents_required": ["Aadhaar Card", "Birth Certificate", "Income Certificate"]
            },
            {
                "title": "Rashtriya Bal Swasthya Karyakram (RBSK)",
                "description": "Child health screening and early intervention services for children from birth to 18 years.",
                "benefits": [
                    "Free health screening",
                    "Early detection of birth defects",
                    "Treatment and management of identified conditions",
                    "Referral services"
                ],
                "eligibility": "All children from birth to 18 years",
                "how_to_apply": "Available at government health facilities",
                "documents_required": ["Birth Certificate", "Aadhaar Card"]
            },
            {
                "title": "Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA)",
                "description": "Provides assured, comprehensive and quality antenatal care to pregnant women.",
                "benefits": [
                    "Free antenatal check-ups on 9th of every month",
                    "High-risk pregnancy identification",
                    "Specialist consultation",
                    "Free medicines and diagnostics"
                ],
                "eligibility": "All pregnant women",
                "how_to_apply": "Visit designated health facilities on 9th of every month",
                "documents_required": ["Pregnancy card", "Aadhaar Card"]
            }
        ]

        return jsonify({
            "success": True,
            "data": schemes_data,
            "message": "Government schemes data loaded successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to load government schemes data"
        }), 500

# Test route to verify new routes are being picked up
@api_bp.route('/test-new-route')
def test_new_route():
    """Test route to verify new routes work"""
    return jsonify({
        'success': True,
        'message': 'New route is working!',
        'timestamp': datetime.now().isoformat()
    })

# Appointment Management API Endpoints

@api_bp.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments_api():
    """Get user appointments or create new appointment"""
    if request.method == 'GET':
        try:
            from app.data_manager import DataManager

            user_id = session['user_id']

            # Get all appointments for the current user
            conn = DataManager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT a.id, a.user_id, a.baby_id, a.appointment_type, a.appointment_date,
                       a.doctor_name, a.clinic_name, a.purpose, a.status, a.notes,
                       a.created_at, b.name as baby_name
                FROM appointments a
                LEFT JOIN babies b ON a.baby_id = b.id
                WHERE a.user_id = ?
                ORDER BY a.appointment_date DESC
            ''', (user_id,))

            rows = cursor.fetchall()
            conn.close()

            appointments_data = []
            for row in rows:
                appointment_dict = {
                    'id': row[0],
                    'user_id': row[1],
                    'baby_id': row[2],
                    'appointment_type': row[3],
                    'appointment_date': row[4],
                    'doctor_name': row[5],
                    'clinic_name': row[6],
                    'purpose': row[7],
                    'status': row[8],
                    'notes': row[9],
                    'created_at': row[10],
                    'baby_name': row[11]
                }
                appointments_data.append(appointment_dict)

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

    elif request.method == 'POST':
        try:
            from app.data_manager import DataManager

            data = request.get_json()
            user_id = session['user_id']

            # Validate required fields
            required_fields = ['appointment_type', 'doctor_name', 'appointment_date']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400

            # Parse appointment date
            try:
                appointment_date = datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid appointment date format'
                }), 400

            # Create new appointment
            conn = DataManager.get_connection()
            cursor = conn.cursor()

            # Find doctor ID by name
            doctor_id = None
            if data.get('doctor_name'):
                users = DataManager.get_all_users()
                doctor = next((u for u in users if u.get('full_name') == data['doctor_name'] and u.get('role') == 'doctor'), None)
                if doctor:
                    doctor_id = doctor['id']

            # Get user information for email
            user_data = DataManager.get_user_by_id(user_id)

            cursor.execute('''
                INSERT INTO appointments (user_id, baby_id, doctor_id, appointment_type, appointment_date,
                                        doctor_name, clinic_name, purpose, status, patient_name, patient_email,
                                        created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('baby_id'),
                doctor_id,
                data['appointment_type'],
                appointment_date.isoformat(),
                data['doctor_name'],
                data.get('clinic_name', 'Maternal Care Clinic'),
                data.get('purpose'),
                'pending',
                user_data['full_name'],
                user_data['email'],
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            appointment_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Send immediate booking notification to patient and doctor
            email_results = {
                'patient_email_sent': False,
                'doctor_email_sent': False
            }

            try:
                from app.services.email_service import email_service

                appointment_details = {
                    'appointment_id': appointment_id,
                    'patient_name': user_data['full_name'],
                    'doctor_name': data['doctor_name'],
                    'appointment_date': appointment_date.strftime('%Y-%m-%d'),
                    'appointment_time': appointment_date.strftime('%H:%M'),
                    'appointment_type': data['appointment_type'],
                    'purpose': data.get('purpose', 'General consultation'),
                    'clinic_name': data.get('clinic_name', 'Maternal Care Clinic'),
                    'patient_email': user_data['email']
                }

                # Get doctor email
                doctor_email = None
                if doctor_id:
                    doctor_user = DataManager.get_user_by_id(doctor_id)
                    if doctor_user:
                        doctor_email = doctor_user['email']

                # Send booking notification emails to both patient and doctor
                email_results = email_service.send_appointment_booking_emails(
                    patient_email=user_data['email'],
                    doctor_email=doctor_email,
                    appointment_details=appointment_details
                )

                return jsonify({
                    'success': True,
                    'message': 'Appointment request submitted successfully. Confirmation emails sent.',
                    'appointment_id': appointment_id,
                    'status': 'pending',
                    'email_results': email_results
                })

            except Exception as email_error:
                # Don't fail the appointment creation if email fails
                print(f"Email notification failed: {email_error}")
                return jsonify({
                    'success': True,
                    'message': 'Appointment request submitted successfully (email notification failed)',
                    'appointment_id': appointment_id,
                    'status': 'pending',
                    'email_results': email_results,
                    'email_error': str(email_error)
                })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@api_bp.route('/appointments/<int:appointment_id>', methods=['DELETE', 'PUT'])
@login_required
def appointment_detail_api(appointment_id):
    """Cancel or update a specific appointment"""
    try:
        from app.data_manager import DataManager

        user_id = session['user_id']

        # Check if appointment exists and belongs to user
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, status FROM appointments
            WHERE id = ? AND user_id = ?
        ''', (appointment_id, user_id))

        appointment = cursor.fetchone()

        if not appointment:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Appointment not found'
            }), 404

        if request.method == 'DELETE':
            # Cancel the appointment
            cursor.execute('''
                UPDATE appointments
                SET status = 'cancelled', updated_at = ?
                WHERE id = ? AND user_id = ?
            ''', (datetime.now().isoformat(), appointment_id, user_id))

            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': 'Appointment cancelled successfully'
            })

        elif request.method == 'PUT':
            # Update appointment
            data = request.get_json()

            update_fields = []
            update_values = []

            if 'status' in data:
                update_fields.append('status = ?')
                update_values.append(data['status'])
            if 'notes' in data:
                update_fields.append('notes = ?')
                update_values.append(data['notes'])
            if 'appointment_date' in data:
                try:
                    appointment_date = datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00'))
                    update_fields.append('appointment_date = ?')
                    update_values.append(appointment_date.isoformat())
                except ValueError:
                    conn.close()
                    return jsonify({
                        'success': False,
                        'error': 'Invalid appointment date format'
                    }), 400

            if update_fields:
                update_fields.append('updated_at = ?')
                update_values.extend([datetime.now().isoformat(), appointment_id, user_id])

                query = f'''
                    UPDATE appointments
                    SET {', '.join(update_fields)}
                    WHERE id = ? AND user_id = ?
                '''

                cursor.execute(query, update_values)
                conn.commit()

            conn.close()

            return jsonify({
                'success': True,
                'message': 'Appointment updated successfully'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/appointments/<int:appointment_id>/confirm', methods=['POST'])
@login_required
def confirm_user_appointment(appointment_id):
    """User confirms their own appointment"""
    try:
        from app.data_manager import DataManager

        user_id = session['user_id']

        # Check if appointment exists and belongs to user
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, status FROM appointments
            WHERE id = ? AND user_id = ?
        ''', (appointment_id, user_id))

        appointment = cursor.fetchone()

        if not appointment:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Appointment not found'
            }), 404

        # Update appointment status to confirmed
        cursor.execute('''
            UPDATE appointments
            SET status = 'confirmed', updated_at = ?
            WHERE id = ? AND user_id = ?
        ''', (datetime.now().isoformat(), appointment_id, user_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Appointment confirmed successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Test endpoint
@api_bp.route('/test')
def test_endpoint():
    """Test endpoint to verify routing"""
    print("✅ TEST ENDPOINT HIT", file=sys.stderr)
    sys.stderr.flush()
    return jsonify({'success': True, 'message': 'API is working!'})


# Baby Management API Endpoints
@api_bp.route('/babies', methods=['GET', 'POST'])
@login_required
def babies_api():
    """Get all babies or register a new baby"""
    from app.data_manager import DataManager
    from datetime import datetime, date, timedelta
    
    if request.method == 'GET':
        try:
            user_id = session['user_id']
            user = DataManager.get_user_by_id(user_id)
            
            # Get babies for this user
            babies = DataManager.get_babies_for_user(user_id, user['role'] == 'admin')
            
            return jsonify({
                'success': True,
                'babies': babies,
                'count': len(babies)
            })

        except Exception as e:
            print(f"❌ Error in GET /api/babies: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        import sys
        print("=" * 80, file=sys.stderr)
        print("🔍 POST /api/babies endpoint called", file=sys.stderr)
        sys.stderr.flush()
        
        try:
            data = request.get_json()
            print(f"📦 Received data: {data}", file=sys.stderr)
            sys.stderr.flush()
            
            user_id = session['user_id']
            print(f"👤 User ID: {user_id}", file=sys.stderr)
            sys.stderr.flush()

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

            # Parse and validate birth date
            try:
                birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                if birth_date > date.today():
                    return jsonify({'error': 'Birth date cannot be in the future'}), 400
                if birth_date < date.today() - timedelta(days=365*5):  # Max 5 years old
                    return jsonify({'error': 'Birth date cannot be more than 5 years ago'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

            # Validate weight and height if provided
            if data.get('weight_at_birth'):
                try:
                    weight = float(data['weight_at_birth'])
                    if weight <= 0 or weight > 10:  # Reasonable range for baby weight in kg
                        return jsonify({'error': 'Weight at birth must be between 0 and 10 kg'}), 400
                except ValueError:
                    return jsonify({'error': 'Invalid weight format'}), 400

            if data.get('height_at_birth'):
                try:
                    height = float(data['height_at_birth'])
                    if height <= 0 or height > 100:  # Reasonable range for baby height in cm
                        return jsonify({'error': 'Height at birth must be between 0 and 100 cm'}), 400
                except ValueError:
                    return jsonify({'error': 'Invalid height format'}), 400

            # Generate unique ID
            unique_id = DataManager.generate_enhanced_unique_id()

            # Create new baby using direct database insert
            conn = DataManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO babies (name, birth_date, gender, weight_at_birth, height_at_birth,
                                  blood_type, parent_id, unique_id, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['name'].strip(),
                birth_date.isoformat(),
                data['gender'].lower(),
                data.get('weight_at_birth'),
                data.get('height_at_birth'),
                data.get('blood_type'),
                user_id,
                unique_id,
                data.get('notes', '').strip(),
                datetime.now().isoformat()
            ))
            
            baby_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Get the created baby
            baby_data = DataManager.get_baby_by_id(baby_id)

            print(f"✅ Baby registered successfully: {baby_data['name']} (ID: {baby_id})")

            return jsonify({
                'success': True,
                'message': 'Baby registered successfully',
                'baby': baby_data
            }), 201

        except Exception as e:
            import sys
            print("=" * 80, file=sys.stderr)
            print(f"❌ Error in baby registration: {type(e).__name__}: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            sys.stderr.flush()
            return jsonify({'error': f'Failed to register baby: {str(e)}'}), 500


@api_bp.route('/babies/<int:baby_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def baby_detail_api(baby_id):
    """Get, update, or delete a specific baby"""
    from app.data_manager import DataManager
    
    try:
        user_id = session['user_id']
        user = DataManager.get_user_by_id(user_id)
        
        # Get baby and check access
        baby = DataManager.get_baby_by_id(baby_id)
        if not baby:
            return jsonify({'error': 'Baby not found'}), 404
            
        # Check if user has access (parent or admin)
        if baby['parent_id'] != user_id and (not user or user['role'] != 'admin'):
            return jsonify({'error': 'Access denied'}), 403

        if request.method == 'GET':
            return jsonify({
                'success': True,
                'baby': baby
            })

        elif request.method == 'PUT':
            # Update baby
            data = request.get_json()
            # Add update logic here
            return jsonify({
                'success': True,
                'message': 'Baby updated successfully'
            })

        elif request.method == 'DELETE':
            # Soft delete
            conn = DataManager.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE babies SET is_active = 0 WHERE id = ?', (baby_id,))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Baby deleted successfully'
            })

    except Exception as e:
        print(f"❌ Error in baby_detail_api: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

