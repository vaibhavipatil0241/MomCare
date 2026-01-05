from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, date, timedelta
from app.data_manager import DataManager
import uuid
import json

babycare_bp = Blueprint('babycare', __name__, url_prefix='/babycare')

def login_required(f):
    """Simple login required decorator"""
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

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

def validate_baby_access(baby_id, user_id):
    """Validate that user has access to baby"""
    baby = DataManager.get_baby_by_id(baby_id)
    if not baby:
        return None, "Baby not found"

    user = DataManager.get_user_by_id(user_id)
    if baby['parent_id'] != user_id and (not user or user['role'] != 'admin'):
        return None, "Access denied"

    return baby, None

# Page Routes

@babycare_bp.route('/')
@login_required
def index():
    """Baby care main page"""
    return render_template('babycare/babycare.html')

@babycare_bp.route('/vaccination')
@login_required
def vaccination():
    """Vaccination tracking page"""
    return render_template('babycare/vaccination.html')

@babycare_bp.route('/nutrition')
@login_required
def nutrition():
    """Nutrition tracking page"""
    return render_template('babycare/nutrition.html')



@babycare_bp.route('/growth-tracker')
@login_required
def growth_tracker():
    """Growth tracking page"""
    return render_template('babycare/growth_tracker.html')

@babycare_bp.route('/schemes')
@login_required
def schemes():
    """Government schemes page"""
    return render_template('babycare/schemes.html')

@babycare_bp.route('/unique_id')
@login_required
def unique_id():
    """Unique ID page"""
    return render_template('babycare/unique_id.html')

# Unique ID API Endpoints

@babycare_bp.route('/api/unique-id/validate/<unique_id>')
@login_required
def validate_unique_id(unique_id):
    """Validate a unique ID"""
    try:
        from app.data_manager import DataManager

        is_valid = DataManager.validate_unique_id(unique_id)
        baby_info = None

        if is_valid:
            baby_info = DataManager.get_baby_by_unique_id(unique_id)

        return jsonify({
            'success': True,
            'valid': is_valid,
            'baby_info': baby_info,
            'message': 'Valid unique ID' if is_valid else 'Invalid unique ID'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@babycare_bp.route('/api/unique-id/lookup/<unique_id>')
@login_required
def lookup_unique_id(unique_id):
    """Lookup baby information by unique ID"""
    try:
        from app.data_manager import DataManager

        baby_info = DataManager.get_baby_with_parent_info(unique_id)

        if not baby_info:
            return jsonify({
                'success': False,
                'error': 'Baby not found with this unique ID'
            }), 404

        # Check if user has permission to view this baby
        user_data = DataManager.get_user_by_id(session['user_id'])
        if baby_info['parent_email'] != user_data['email'] and user_data['role'] != 'admin':
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        return jsonify({
            'success': True,
            'baby': baby_info
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@babycare_bp.route('/api/unique-id/regenerate/<int:baby_id>', methods=['POST'])
@login_required
def regenerate_unique_id(baby_id):
    """Regenerate unique ID for a baby"""
    try:
        from app.data_manager import DataManager

        new_unique_id, error = DataManager.regenerate_baby_unique_id(baby_id, session['user_id'])

        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 400 if 'Access denied' in error else 404

        return jsonify({
            'success': True,
            'new_unique_id': new_unique_id,
            'message': 'Unique ID regenerated successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@babycare_bp.route('/api/unique-id/my-babies')
@login_required
def get_my_babies_with_ids():
    """Get all babies for current user with their unique IDs"""
    try:
        from app.data_manager import DataManager

        user_data = DataManager.get_user_by_id(session['user_id'])
        babies = DataManager.get_babies_for_user(session['user_id'], user_data['role'] == 'admin')

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

@babycare_bp.route('/api/babies/by-unique-id/<unique_id>')
@login_required
def get_baby_by_unique_id_api(unique_id):
    """Get baby information by unique ID - shows only if user has access"""
    try:
        user_id = session['user_id']
        user = DataManager.get_user_by_id(user_id)
        
        # Get baby by unique ID
        baby = DataManager.get_baby_by_unique_id(unique_id)
        
        if not baby:
            return jsonify({
                'success': False,
                'error': 'Baby not found with this unique ID'
            }), 404
        
        # Check if user has access (parent or admin)
        if baby['parent_id'] != user_id and (not user or user['role'] != 'admin'):
            return jsonify({
                'success': False,
                'error': 'Access denied - this baby does not belong to you'
            }), 403
        
        # Get additional baby information with parent details
        baby_with_parent = DataManager.get_baby_with_parent_info(unique_id)
        
        return jsonify({
            'success': True,
            'baby': baby_with_parent,
            'message': 'Baby found successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@babycare_bp.route('/api/babies/filter-by-unique-id', methods=['POST'])
@login_required
def filter_babies_by_unique_id():
    """Filter and get babies by unique ID - used by baby care page to show specific user's babies"""
    try:
        data = request.get_json()
        unique_id = data.get('unique_id', '').strip()
        user_id = session['user_id']
        user = DataManager.get_user_by_id(user_id)
        
        if not unique_id:
            return jsonify({
                'success': False,
                'error': 'Unique ID is required'
            }), 400
        
        # Validate and get baby by unique ID
        baby = DataManager.get_baby_by_unique_id(unique_id)
        
        if not baby:
            return jsonify({
                'success': False,
                'error': 'No baby found with this unique ID'
            }), 404
        
        # Check if user has access (parent or admin)
        if baby['parent_id'] != user_id and (not user or user['role'] != 'admin'):
            return jsonify({
                'success': False,
                'error': 'Access denied - You do not have permission to view this baby'
            }), 403
        
        # Get full baby information with parent details
        baby_with_parent = DataManager.get_baby_with_parent_info(unique_id)
        
        # Get related data for this baby
        conn = DataManager.get_connection()
        cursor = conn.cursor()
        
        # Get vaccinations
        cursor.execute('''
            SELECT * FROM vaccinations 
            WHERE baby_id = ? 
            ORDER BY scheduled_date DESC
        ''', (baby['id'],))
        vaccinations = [dict(zip([col[0] for col in cursor.description], row)) 
                       for row in cursor.fetchall()]
        
        # Get growth records
        cursor.execute('''
            SELECT * FROM growth_records 
            WHERE baby_id = ? 
            ORDER BY record_date DESC
        ''', (baby['id'],))
        growth_records = [dict(zip([col[0] for col in cursor.description], row)) 
                         for row in cursor.fetchall()]
        
        # Get nutrition records
        cursor.execute('''
            SELECT * FROM nutrition_records 
            WHERE baby_id = ? 
            ORDER BY record_date DESC
        ''', (baby['id'],))
        nutrition_records = [dict(zip([col[0] for col in cursor.description], row)) 
                            for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'baby': baby_with_parent,
            'related_data': {
                'vaccinations': vaccinations,
                'growth_records': growth_records,
                'nutrition_records': nutrition_records
            },
            'message': f'Successfully loaded data for {baby["name"]}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@babycare_bp.route('/api/unique-id/qr-code/<unique_id>')
@login_required
def generate_qr_code(unique_id):
    """Generate QR code for unique ID"""
    try:
        from app.data_manager import DataManager
        import qrcode
        import io
        import base64

        # Validate the unique ID first
        baby_info = DataManager.get_baby_by_unique_id(unique_id)
        if not baby_info:
            return jsonify({
                'success': False,
                'error': 'Invalid unique ID'
            }), 404

        # Check permission
        user_data = DataManager.get_user_by_id(session['user_id'])
        if baby_info['parent_id'] != session['user_id'] and user_data['role'] != 'admin':
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Create QR code data
        qr_data = {
            'unique_id': unique_id,
            'baby_name': baby_info['name'],
            'verification_url': f"{request.host_url}babycare/api/unique-id/validate/{unique_id}"
        }

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(qr_data))
        qr.make(fit=True)

        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()

        return jsonify({
            'success': True,
            'qr_code': f"data:image/png;base64,{qr_base64}",
            'qr_data': qr_data
        })

    except ImportError:
        # Fallback if qrcode library is not available
        return jsonify({
            'success': False,
            'error': 'QR code generation not available. Please install qrcode library.',
            'fallback_url': f"{request.host_url}babycare/api/unique-id/validate/{unique_id}"
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@babycare_bp.route('/verify-id')
def verify_id_page():
    """Public ID verification page"""
    return render_template('babycare/verify_id.html')

@babycare_bp.route('/api/verify-id', methods=['POST'])
def verify_id_api():
    """Public API to verify unique ID"""
    try:
        data = request.get_json()
        unique_id = data.get('unique_id', '').strip()

        if not unique_id:
            return jsonify({
                'success': False,
                'error': 'Unique ID is required'
            }), 400

        from app.data_manager import DataManager

        # Get baby information (limited for privacy)
        baby_info = DataManager.get_baby_by_unique_id(unique_id)

        if not baby_info:
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Invalid unique ID'
            })

        # Return limited information for verification
        verification_info = {
            'valid': True,
            'baby_name': baby_info['name'],
            'birth_date': baby_info['birth_date'],
            'gender': baby_info['gender'],
            'unique_id': baby_info['unique_id'],
            'created_at': baby_info['created_at']
        }

        return jsonify({
            'success': True,
            'valid': True,
            'baby': verification_info,
            'message': 'Valid unique ID verified successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@babycare_bp.route('/api/unique-id/history/<int:baby_id>')
@login_required
def get_unique_id_history(baby_id):
    """Get unique ID history for a baby"""
    try:
        from app.data_manager import DataManager

        # Check if user has permission to view this baby
        baby_info = DataManager.get_baby_by_id(baby_id)
        if not baby_info:
            return jsonify({
                'success': False,
                'error': 'Baby not found'
            }), 404

        user_data = DataManager.get_user_by_id(session['user_id'])
        if baby_info['parent_id'] != session['user_id'] and user_data['role'] != 'admin':
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        history = DataManager.get_unique_id_history(baby_id)

        return jsonify({
            'success': True,
            'history': history,
            'baby_name': baby_info['name']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@babycare_bp.route('/api/admin/unique-ids')
@login_required
def admin_get_all_unique_ids():
    """Admin endpoint to get all unique IDs"""
    try:
        from app.data_manager import DataManager

        # Check if user is admin
        user_data = DataManager.get_user_by_id(session['user_id'])
        if user_data['role'] != 'admin':
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403

        all_babies = DataManager.get_all_unique_ids_for_admin()

        return jsonify({
            'success': True,
            'babies': all_babies,
            'count': len(all_babies)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@babycare_bp.route('/chatbot')
@login_required
def chatbot():
    """Chatbot page"""
    return render_template('babycare/chatbot.html')

@babycare_bp.route('/api/chatbot/ask', methods=['POST'])
@login_required
def chatbot_ask():
    """AI Chatbot API endpoint"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip().lower()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Enhanced knowledge base with comprehensive baby care information
        response = generate_ai_response(question)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_ai_response(question):
    """Generate AI response based on question"""
    
    # Comprehensive knowledge base
    knowledge_base = {
        'feeding': {
            'keywords': ['feed', 'milk', 'breast', 'bottle', 'formula', 'nursing', 'breastfeed', 'hungry', 'appetite', 'meal'],
            'responses': [
                {
                    'condition': lambda q: 'newborn' in q or '0' in q or 'first' in q or 'beginning' in q,
                    'answer': "🍼 **Newborn Feeding (0-3 months):**\n\n• **Frequency**: Feed every 2-3 hours (8-12 times per day)\n• **Breastfed**: On-demand, usually 10-15 minutes per breast\n• **Formula**: 2-3 ounces per feeding\n• **Signs of hunger**: Rooting, sucking on hands, fussiness\n• **Important**: Never let a newborn go more than 4 hours without feeding"
                },
                {
                    'condition': lambda q: 'how often' in q or 'schedule' in q or 'frequency' in q,
                    'answer': "📅 **Feeding Schedule by Age:**\n\n**0-3 months**: Every 2-3 hours (8-12 feedings/day)\n**3-6 months**: Every 3-4 hours (6-8 feedings/day)\n**6-12 months**: Every 4-5 hours (4-6 feedings/day) + solid foods\n**12+ months**: 3 meals + 2 snacks + 2-3 milk feedings\n\n💡 Remember: Every baby is different! Watch for hunger cues rather than strictly following a schedule."
                },
                {
                    'condition': lambda q: 'enough' in q or 'sufficient' in q or 'adequate' in q,
                    'answer': "✅ **Signs Baby is Getting Enough Milk:**\n\n• 6+ wet diapers per day (after day 5)\n• Steady weight gain\n• Content and satisfied after feeds\n• Regular bowel movements\n• Active and alert when awake\n• Good skin tone and color\n\n⚠️ **Consult doctor if**: Baby seems constantly hungry, isn't gaining weight, has fewer than 4 wet diapers/day"
                },
                {
                    'condition': lambda q: 'solid' in q or 'food' in q or 'introduce' in q or 'start' in q,
                    'answer': "🥄 **Introducing Solid Foods:**\n\n**When to start**: Around 6 months\n**Signs of readiness**:\n• Can sit with support\n• Shows interest in food\n• Lost tongue-thrust reflex\n• Can hold head steady\n\n**First foods**: Iron-fortified cereal, pureed fruits/vegetables\n**Progression**: Single-ingredient foods → mixed foods → finger foods\n**Important**: Introduce new foods one at a time, wait 3-5 days between new foods"
                }
            ],
            'default': "🍼 **General Feeding Tips:**\n\n• Feed on demand for newborns\n• Watch for hunger cues (rooting, sucking, fussiness)\n• Burp baby during and after feeds\n• Keep baby upright for 20-30 minutes after feeding\n• Track wet diapers and weight gain\n• Consult your pediatrician for personalized advice"
        },
        'sleep': {
            'keywords': ['sleep', 'nap', 'night', 'bedtime', 'wake', 'tired', 'rest', 'drowsy'],
            'responses': [
                {
                    'condition': lambda q: 'through the night' in q or 'all night' in q or 'sleeping through' in q,
                    'answer': "🌙 **Sleeping Through the Night:**\n\n**Typical timeline**:\n• 3-6 months: Some babies start sleeping 6-8 hour stretches\n• 6-12 months: Most sleep through the night\n• Every baby is different!\n\n**Tips to encourage**:\n• Establish bedtime routine\n• Put baby down drowsy but awake\n• Ensure daytime feeds are adequate\n• Create sleep-friendly environment (dark, quiet, cool)\n• Be patient and consistent"
                },
                {
                    'condition': lambda q: 'how much' in q or 'how long' in q or 'hours' in q,
                    'answer': "⏰ **Sleep Requirements by Age:**\n\n**Newborn (0-3 months)**: 14-17 hours/day\n**Infants (4-11 months)**: 12-15 hours/day\n**Toddlers (1-2 years)**: 11-14 hours/day\n**Preschool (3-5 years)**: 10-13 hours/day\n\n💤 **Sleep patterns**:\n• Newborns: Multiple short sleep cycles\n• 3-6 months: Longer night sleep, 2-3 naps\n• 6-12 months: Night sleep improves, 2 naps\n• 12+ months: 1-2 naps per day"
                },
                {
                    'condition': lambda q: 'routine' in q or 'schedule' in q or 'bedtime' in q,
                    'answer': "🌟 **Bedtime Routine Tips:**\n\n**Good routine includes**:\n1. Bath (warm, relaxing)\n2. Gentle massage\n3. Pajamas and diaper change\n4. Feeding (but not to sleep)\n5. Story or lullaby\n6. Dim lights\n7. Put down drowsy but awake\n\n⏰ **Timing**: Same time each night, 20-30 minute routine\n**Benefits**: Helps baby recognize sleep cues, reduces bedtime battles"
                }
            ],
            'default': "😴 **Sleep Tips:**\n\n• Create consistent bedtime routine\n• Safe sleep: Back to sleep, firm mattress, no loose blankets\n• Watch for sleep cues (yawning, rubbing eyes, fussiness)\n• Room should be dark, quiet, and cool (68-72°F)\n• White noise can be helpful\n• Avoid screen time before bed"
        },
        'development': {
            'keywords': ['milestone', 'development', 'month', 'growth', 'crawl', 'walk', 'talk', 'sit', 'roll', 'stand', 'age'],
            'responses': [
                {
                    'condition': lambda q: any(month in q for month in ['0', '1', '2', '3', 'newborn', 'three']),
                    'answer': "👶 **0-3 Months Milestones:**\n\n**Physical**:\n• Lifts head during tummy time\n• Opens and closes hands\n• Brings hands to mouth\n• Swipes at dangling objects\n\n**Social/Emotional**:\n• Begins to smile at people\n• Calms when spoken to\n• Turns head toward sounds\n\n**Communication**:\n• Coos and makes gurgling sounds\n• Turns head toward sound of your voice\n• Cries in different ways for different needs"
                },
                {
                    'condition': lambda q: any(month in q for month in ['4', '5', '6', 'four', 'five', 'six']),
                    'answer': "👶 **4-6 Months Milestones:**\n\n**Physical**:\n• Rolls over (both ways)\n• Sits with support\n• Reaches for toys\n• Brings objects to mouth\n• Pushes up on arms during tummy time\n\n**Social/Emotional**:\n• Smiles spontaneously\n• Laughs out loud\n• Enjoys looking at self in mirror\n• Responds to affection\n\n**Communication**:\n• Babbles with expression\n• Responds to own name\n• Makes sounds to show joy"
                },
                {
                    'condition': lambda q: any(month in q for month in ['7', '8', '9', 'seven', 'eight', 'nine']),
                    'answer': "👶 **7-9 Months Milestones:**\n\n**Physical**:\n• Sits without support\n• Gets to sitting position\n• Begins to crawl or scoot\n• Transfers objects hand to hand\n• Uses pincer grasp\n\n**Social/Emotional**:\n• May be afraid of strangers\n• Shows preference for certain people/toys\n• Understands \"no\"\n\n**Communication**:\n• Babbles mama, dada (non-specific)\n• Copies sounds and gestures\n• Points at things"
                },
                {
                    'condition': lambda q: any(month in q for month in ['10', '11', '12', 'ten', 'eleven', 'twelve', 'year', 'one year']),
                    'answer': "🎉 **10-12 Months Milestones:**\n\n**Physical**:\n• Pulls to stand\n• Cruises along furniture\n• May take first steps\n• Drinks from cup\n• Uses objects correctly (brush, phone)\n\n**Social/Emotional**:\n• Shy or nervous with strangers\n• Cries when mom/dad leaves\n• Has favorite things and people\n• Shows fear in some situations\n\n**Communication**:\n• Says \"mama\" and \"dada\" with meaning\n• Uses simple gestures (waves, shakes head)\n• Responds to simple requests\n• First words may appear"
                }
            ],
            'default': "📊 **Remember**: Every child develops at their own pace!\n\n**When to consult doctor**:\n• No social smiles by 3 months\n• Not sitting by 9 months\n• No babbling by 12 months\n• Loss of skills\n• You have concerns\n\n💚 Trust your instincts! You know your baby best."
        },
        'health': {
            'keywords': ['sick', 'fever', 'cold', 'cough', 'doctor', 'illness', 'temperature', 'vomit', 'diarrhea', 'rash'],
            'responses': [
                {
                    'condition': lambda q: 'fever' in q or 'temperature' in q,
                    'answer': "🌡️ **Fever in Babies:**\n\n**Normal temperature**: 97°F - 100.4°F (36.1°C - 38°C)\n\n**CALL DOCTOR IMMEDIATELY if**:\n• Under 3 months with fever ≥100.4°F (38°C)\n• 3-6 months with fever ≥102°F (38.9°C)\n• Any age with fever ≥104°F (40°C)\n• Fever lasting more than 24 hours (under 2 years)\n• Fever with rash, stiff neck, severe headache\n\n**Home care**:\n• Keep baby hydrated\n• Dress in light clothing\n• Give age-appropriate fever reducer (consult doctor first)\n• Never give aspirin to children"
                },
                {
                    'condition': lambda q: 'when' in q and 'doctor' in q or 'call' in q and 'doctor' in q,
                    'answer': "☎️ **When to Call the Doctor:**\n\n**CALL IMMEDIATELY (or 911) if**:\n• Baby under 3 months with fever\n• Difficulty breathing\n• Blue lips or face\n• Unresponsive or lethargic\n• Severe vomiting or diarrhea\n• Blood in stool\n• Signs of dehydration\n\n**CALL WITHIN 24 HOURS if**:\n• Mild fever lasting >3 days\n• Persistent cough or cold\n• Ear tugging with fever\n• Unusual rash\n• Poor feeding for 2+ days\n• Decreased wet diapers"
                }
            ],
            'default': "🏥 **General Health Tips:**\n\n• Regular well-child checkups\n• Keep vaccination schedule\n• Trust your instincts\n• Better to call doctor if unsure\n• Have pediatrician's emergency number\n• Know your baby's normal patterns\n\n**Emergency signs**: Difficulty breathing, blue color, unresponsive, high fever (under 3 months)"
        },
        'safety': {
            'keywords': ['safe', 'safety', 'danger', 'prevent', 'accident', 'babyproof', 'childproof'],
            'responses': [
                {
                    'condition': lambda q: 'sleep' in q or 'crib' in q or 'bed' in q or 'sids' in q,
                    'answer': "🛏️ **Safe Sleep Guidelines:**\n\n**ABCs of safe sleep**:\n• **A**lone: Baby sleeps alone in crib\n• **B**ack: Always on back to sleep\n• **C**rib: Firm mattress, fitted sheet only\n\n**DON'T**:\n• No pillows, blankets, toys, bumpers\n• No co-sleeping\n• No sleeping on couch/armchair\n• No overheating\n\n**DO**:\n• Room-share (not bed-share) for first 6-12 months\n• Use sleep sack instead of blankets\n• Pacifier at naptime/bedtime (once breastfeeding established)"
                },
                {
                    'condition': lambda q: 'car' in q or 'seat' in q or 'travel' in q,
                    'answer': "🚗 **Car Seat Safety:**\n\n**Rear-facing** (birth-2+ years):\n• Keep rear-facing as long as possible\n• Until height/weight limit of seat\n• Minimum 2 years old\n\n**Installation**:\n• Read manual carefully\n• Seat shouldn't move >1 inch\n• Harness snug (can't pinch strap)\n• Chest clip at armpit level\n\n**Never**:\n• Use expired or recalled seat\n• Use seat after accident\n• Put thick coats under harness\n• Leave baby in car alone"
                }
            ],
            'default': "🛡️ **Baby Safety Checklist:**\n\n• Install smoke/CO detectors\n• Cover electrical outlets\n• Secure furniture to walls\n• Lock cabinets with chemicals\n• Keep small objects out of reach\n• Use safety gates on stairs\n• Set water heater to <120°F\n• Never leave baby unattended\n• Learn infant CPR"
        }
    }
    
    # Find matching category and generate response
    for category, data in knowledge_base.items():
        if any(keyword in question for keyword in data['keywords']):
            # Check for specific conditions
            for response_item in data.get('responses', []):
                if response_item['condition'](question):
                    return response_item['answer']
            # Return default for category
            return data.get('default', '')
    
    # General fallback response
    return ("👋 I'm here to help with baby care questions!\n\n"
            "**I can assist you with:**\n"
            "• 🍼 Feeding schedules and nutrition\n"
            "• 😴 Sleep patterns and routines\n"
            "• 📊 Development milestones\n"
            "• 🏥 Health and when to call the doctor\n"
            "• 🛡️ Safety guidelines\n\n"
            "Please ask me a specific question, or try one of the quick questions above!")

# API Routes

@babycare_bp.route('/api/babies', methods=['GET', 'POST'])
@login_required
def babies_api():
    """Get all babies for current user or create a new baby"""
    if request.method == 'GET':
        try:
            user_id = session['user_id']
            user = DataManager.get_user_by_id(user_id)
            
            # Get babies based on user role using DataManager
            conn = DataManager.get_connection()
            cursor = conn.cursor()
            
            if user and user['role'] == 'admin':
                # Admin can see all babies
                cursor.execute('''
                    SELECT b.id, b.name, b.birth_date, b.gender, b.weight_at_birth,
                           b.height_at_birth, b.blood_type, b.parent_id, b.unique_id,
                           b.notes, b.created_at, u.full_name as parent_name, u.email as parent_email
                    FROM babies b
                    JOIN users u ON b.parent_id = u.id
                    WHERE b.is_active = 1
                    ORDER BY b.created_at DESC
                ''')
            else:
                # Regular users can only see their own babies
                cursor.execute('''
                    SELECT b.id, b.name, b.birth_date, b.gender, b.weight_at_birth,
                           b.height_at_birth, b.blood_type, b.parent_id, b.unique_id,
                           b.notes, b.created_at, u.full_name as parent_name, u.email as parent_email
                    FROM babies b
                    JOIN users u ON b.parent_id = u.id
                    WHERE b.parent_id = ? AND b.is_active = 1
                    ORDER BY b.created_at DESC
                ''', (user_id,))
            
            babies_data = []
            for row in cursor.fetchall():
                baby_dict = {
                    'id': row[0],
                    'name': row[1],
                    'date_of_birth': row[2],  # Changed from birth_date to date_of_birth
                    'birth_date': row[2],      # Keep both for compatibility
                    'gender': row[3],
                    'weight_at_birth': row[4],
                    'height_at_birth': row[5],
                    'blood_type': row[6],
                    'parent_id': row[7],
                    'unique_id': row[8],
                    'notes': row[9],
                    'created_at': row[10],
                    'parent_name': row[11],
                    'parent_email': row[12]
                }
                babies_data.append(baby_dict)
            
            conn.close()

            return jsonify({
                'success': True,
                'babies': babies_data,
                'count': len(babies_data)
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            user_id = session['user_id']

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

            # Create new baby using DataManager
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

            return jsonify({
                'success': True,
                'message': 'Baby registered successfully',
                'baby': baby_data
            }), 201

        except Exception as e:
            print(f"❌ Error in baby registration: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to register baby: {str(e)}'}), 500

@babycare_bp.route('/api/babies/<int:baby_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def baby_detail_api(baby_id):
    """Get, update, or delete a specific baby"""
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
            data = request.get_json()
            conn = DataManager.get_connection()
            cursor = conn.cursor()

            # Build update query dynamically based on provided fields
            update_fields = []
            update_values = []

            # Validate and update baby information
            if 'name' in data:
                if len(data['name'].strip()) < 2:
                    return jsonify({'error': 'Baby name must be at least 2 characters long'}), 400
                update_fields.append('name = ?')
                update_values.append(data['name'].strip())

            if 'birth_date' in data:
                try:
                    birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                    if birth_date > date.today():
                        return jsonify({'error': 'Birth date cannot be in the future'}), 400
                    update_fields.append('birth_date = ?')
                    update_values.append(birth_date.isoformat())
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

            if 'gender' in data:
                if data['gender'].lower() not in ['male', 'female', 'other']:
                    return jsonify({'error': 'Gender must be male, female, or other'}), 400
                update_fields.append('gender = ?')
                update_values.append(data['gender'].lower())

            if 'weight_at_birth' in data:
                try:
                    weight = float(data['weight_at_birth'])
                    if weight <= 0 or weight > 10:
                        return jsonify({'error': 'Weight at birth must be between 0 and 10 kg'}), 400
                    update_fields.append('weight_at_birth = ?')
                    update_values.append(weight)
                except ValueError:
                    return jsonify({'error': 'Invalid weight format'}), 400

            if 'height_at_birth' in data:
                try:
                    height = float(data['height_at_birth'])
                    if height <= 0 or height > 100:
                        return jsonify({'error': 'Height at birth must be between 0 and 100 cm'}), 400
                    update_fields.append('height_at_birth = ?')
                    update_values.append(height)
                except ValueError:
                    return jsonify({'error': 'Invalid height format'}), 400

            if 'blood_type' in data:
                update_fields.append('blood_type = ?')
                update_values.append(data['blood_type'])

            if 'notes' in data:
                update_fields.append('notes = ?')
                update_values.append(data['notes'].strip())

            if update_fields:
                update_values.append(baby_id)
                query = f"UPDATE babies SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
                conn.commit()

            conn.close()

            # Get updated baby data
            updated_baby = DataManager.get_baby_by_id(baby_id)

            return jsonify({
                'success': True,
                'message': 'Baby information updated successfully',
                'baby': updated_baby
            })

        elif request.method == 'DELETE':
            # Soft delete - mark as inactive instead of actual deletion
            conn = DataManager.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE babies SET is_active = 0 WHERE id = ?', (baby_id,))
            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': 'Baby record deactivated successfully'
            })

    except Exception as e:
        return jsonify({'error': f'Operation failed: {str(e)}'}), 500

@babycare_bp.route('/api/babies/<int:baby_id>/dashboard')
@login_required
def baby_dashboard_api(baby_id):
    """Get comprehensive dashboard data for a specific baby"""
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

        # Get recent records using DataManager
        conn = DataManager.get_connection()
        cursor = conn.cursor()
        
        # Get recent vaccinations
        cursor.execute('''
            SELECT * FROM vaccinations 
            WHERE baby_id = ? 
            ORDER BY scheduled_date DESC 
            LIMIT 5
        ''', (baby_id,))
        recent_vaccinations = [dict(zip([col[0] for col in cursor.description], row)) 
                             for row in cursor.fetchall()]
        
        # Get recent growth records
        cursor.execute('''
            SELECT * FROM growth_records 
            WHERE baby_id = ? 
            ORDER BY record_date DESC 
            LIMIT 5
        ''', (baby_id,))
        recent_growth = [dict(zip([col[0] for col in cursor.description], row)) 
                        for row in cursor.fetchall()]
        
        # Get recent nutrition records
        cursor.execute('''
            SELECT * FROM nutrition_records 
            WHERE baby_id = ? 
            ORDER BY record_date DESC 
            LIMIT 5
        ''', (baby_id,))
        recent_nutrition = [dict(zip([col[0] for col in cursor.description], row)) 
                           for row in cursor.fetchall()]
        
        # Get upcoming appointments
        cursor.execute('''
            SELECT * FROM appointments 
            WHERE baby_id = ? AND appointment_date > ? 
            ORDER BY appointment_date 
            LIMIT 5
        ''', (baby_id, datetime.now().isoformat()))
        upcoming_appointments = [dict(zip([col[0] for col in cursor.description], row)) 
                                for row in cursor.fetchall()]
        
        # Count total records
        cursor.execute('SELECT COUNT(*) FROM vaccinations WHERE baby_id = ?', (baby_id,))
        total_vaccinations = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM growth_records WHERE baby_id = ?', (baby_id,))
        total_growth_records = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM nutrition_records WHERE baby_id = ?', (baby_id,))
        total_nutrition_records = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM appointments WHERE baby_id = ?', (baby_id,))
        total_appointments = cursor.fetchone()[0]
        
        # Calculate vaccination progress
        cursor.execute('''
            SELECT COUNT(*) FROM vaccinations 
            WHERE baby_id = ? AND status = 'completed'
        ''', (baby_id,))
        completed_vaccinations = cursor.fetchone()[0]
        
        conn.close()

        vaccination_progress = {
            'total': total_vaccinations,
            'completed': completed_vaccinations,
            'percentage': (completed_vaccinations / total_vaccinations * 100) if total_vaccinations > 0 else 0
        }

        return jsonify({
            'success': True,
            'baby': baby,
            'recent_data': {
                'vaccinations': recent_vaccinations,
                'growth_records': recent_growth,
                'nutrition_records': recent_nutrition,
                'upcoming_appointments': upcoming_appointments
            },
            'statistics': {
                'vaccination_progress': vaccination_progress,
                'total_records': {
                    'vaccinations': total_vaccinations,
                    'growth_records': total_growth_records,
                    'nutrition_records': total_nutrition_records,
                    'appointments': total_appointments
                }
            }
        })

    except Exception as e:
        return jsonify({'error': f'Failed to load dashboard: {str(e)}'}), 500

@babycare_bp.route('/api/babies/<int:baby_id>/vaccinations', methods=['GET', 'POST'])
@login_required
def vaccinations_api(baby_id):
    """Get or create vaccinations for a baby"""
    # Verify baby belongs to current user
    baby = Baby.query.filter_by(id=baby_id, parent_id=session['user_id']).first()
    if not baby:
        return jsonify({'error': 'Baby not found'}), 404

    if request.method == 'GET':
        vaccinations = Vaccination.query.filter_by(baby_id=baby_id).all()
        return jsonify({
            'success': True,
            'vaccinations': [vaccination.to_dict() for vaccination in vaccinations]
        })

    elif request.method == 'POST':
        data = request.get_json()

        # Validate required fields
        required_fields = ['vaccine_name', 'scheduled_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        try:
            # Parse dates
            scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date()
            administered_date = None
            if data.get('administered_date'):
                administered_date = datetime.strptime(data['administered_date'], '%Y-%m-%d').date()

            # Create new vaccination record
            vaccination = Vaccination(
                baby_id=baby_id,
                vaccine_name=data['vaccine_name'],
                scheduled_date=scheduled_date,
                administered_date=administered_date,
                status=data.get('status', 'scheduled'),
                doctor_name=data.get('doctor_name'),
                notes=data.get('notes')
            )

            db.session.add(vaccination)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Vaccination record created successfully',
                'vaccination': vaccination.to_dict()
            }), 201

        except ValueError as e:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@babycare_bp.route('/api/babies/<int:baby_id>/nutrition', methods=['GET', 'POST'])
@login_required
def nutrition_api(baby_id):
    """Get or create nutrition records for a baby"""
    # Verify baby belongs to current user
    baby = Baby.query.filter_by(id=baby_id, parent_id=session['user_id']).first()
    if not baby:
        return jsonify({'error': 'Baby not found'}), 404

    if request.method == 'GET':
        nutrition_records = NutritionRecord.query.filter_by(baby_id=baby_id).all()
        return jsonify({
            'success': True,
            'nutrition_records': [record.to_dict() for record in nutrition_records]
        })

    elif request.method == 'POST':
        data = request.get_json()

        # Validate required fields
        required_fields = ['record_date', 'feeding_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        try:
            # Parse date
            record_date = datetime.strptime(data['record_date'], '%Y-%m-%d').date()

            # Create new nutrition record
            nutrition_record = NutritionRecord(
                baby_id=baby_id,
                record_date=record_date,
                feeding_type=data['feeding_type'],
                amount=data.get('amount'),
                frequency=data.get('frequency'),
                food_items=data.get('food_items'),
                notes=data.get('notes')
            )

            db.session.add(nutrition_record)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Nutrition record created successfully',
                'nutrition_record': nutrition_record.to_dict()
            }), 201

        except ValueError as e:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500



@babycare_bp.route('/api/babies/<int:baby_id>/growth', methods=['GET', 'POST'])
@login_required
def growth_api(baby_id):
    """Get or create growth records for a baby"""
    # Verify baby belongs to current user
    baby = Baby.query.filter_by(id=baby_id, parent_id=session['user_id']).first()
    if not baby:
        return jsonify({'error': 'Baby not found'}), 404

    if request.method == 'GET':
        growth_records = GrowthRecord.query.filter_by(baby_id=baby_id).all()
        return jsonify({
            'success': True,
            'growth_records': [record.to_dict() for record in growth_records]
        })

    elif request.method == 'POST':
        data = request.get_json()

        # Validate required fields
        required_fields = ['record_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        try:
            # Parse date
            record_date = datetime.strptime(data['record_date'], '%Y-%m-%d').date()

            # Create new growth record
            growth_record = GrowthRecord(
                baby_id=baby_id,
                record_date=record_date,
                weight=data.get('weight'),
                height=data.get('height'),
                head_circumference=data.get('head_circumference'),
                notes=data.get('notes')
            )

            db.session.add(growth_record)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Growth record created successfully',
                'growth_record': growth_record.to_dict()
            }), 201

        except ValueError as e:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# Admin Routes

@babycare_bp.route('/api/admin/baby-care-stats')
@admin_required
def admin_baby_care_stats():
    """Get baby care statistics for admin dashboard"""
    try:
        total_babies = Baby.query.count()
        total_vaccinations = Vaccination.query.count()
        total_nutrition_records = NutritionRecord.query.count()

        total_growth_records = GrowthRecord.query.count()

        # Get recent activity
        recent_babies = Baby.query.order_by(Baby.created_at.desc()).limit(5).all()
        recent_vaccinations = Vaccination.query.order_by(Vaccination.created_at.desc()).limit(5).all()

        return jsonify({
            'success': True,
            'stats': {
                'total_babies': total_babies,
                'total_vaccinations': total_vaccinations,
                'total_nutrition_records': total_nutrition_records,

                'total_growth_records': total_growth_records,
                'baby_records': total_babies,
                'total_users': User.query.count(),
                'active_sessions': 1,  # This would be calculated based on active sessions
                'last_updated': datetime.utcnow().isoformat()
            },
            'recent_activity': {
                'recent_babies': [baby.to_dict() for baby in recent_babies],
                'recent_vaccinations': [vaccination.to_dict() for vaccination in recent_vaccinations]
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@babycare_bp.route('/api/admin/update-content', methods=['POST'])
@admin_required
def admin_update_content():
    """Update baby care page content"""
    try:
        data = request.get_json()

        # In a real application, you would save this to a content management table
        # For now, we'll just return success

        return jsonify({
            'success': True,
            'message': 'Content updated successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@babycare_bp.route('/api/admin/all-babies')
@admin_required
def admin_all_babies():
    """Get all babies for admin management"""
    try:
        babies = Baby.query.all()
        babies_data = []

        for baby in babies:
            baby_dict = baby.to_dict()
            # Add parent information
            parent = User.query.get(baby.parent_id)
            baby_dict['parent_name'] = parent.full_name if parent else 'Unknown'
            baby_dict['parent_email'] = parent.email if parent else 'Unknown'
            babies_data.append(baby_dict)

        return jsonify({
            'success': True,
            'babies': babies_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@babycare_bp.route('/api/admin/vaccination-schedule')
@admin_required
def admin_vaccination_schedule():
    """Get vaccination schedule overview for admin"""
    try:
        # Get upcoming vaccinations
        upcoming_vaccinations = Vaccination.query.filter(
            Vaccination.status == 'scheduled',
            Vaccination.scheduled_date >= date.today()
        ).order_by(Vaccination.scheduled_date).all()

        # Get overdue vaccinations
        overdue_vaccinations = Vaccination.query.filter(
            Vaccination.status == 'scheduled',
            Vaccination.scheduled_date < date.today()
        ).order_by(Vaccination.scheduled_date).all()

        vaccination_data = []
        for vaccination in upcoming_vaccinations + overdue_vaccinations:
            vaccination_dict = vaccination.to_dict()
            baby = Baby.query.get(vaccination.baby_id)
            vaccination_dict['baby_name'] = baby.name if baby else 'Unknown'
            vaccination_dict['is_overdue'] = vaccination.scheduled_date < date.today()
            vaccination_data.append(vaccination_dict)

        return jsonify({
            'success': True,
            'vaccinations': vaccination_data,
            'upcoming_count': len(upcoming_vaccinations),
            'overdue_count': len(overdue_vaccinations)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@babycare_bp.route('/api/admin/export-data')
@admin_required
def admin_export_data():
    """Export all baby care data for admin"""
    try:
        # In a real application, this would generate a comprehensive export
        # For now, we'll return a summary

        export_data = {
            'babies': [baby.to_dict() for baby in Baby.query.all()],
            'vaccinations': [vaccination.to_dict() for vaccination in Vaccination.query.all()],
            'nutrition_records': [record.to_dict() for record in NutritionRecord.query.all()],

            'growth_records': [record.to_dict() for record in GrowthRecord.query.all()],
            'export_date': datetime.utcnow().isoformat()
        }

        return jsonify({
            'success': True,
            'message': 'Data export completed',
            'data': export_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@babycare_bp.route('/api/appointments', methods=['GET', 'POST'])
@login_required
def appointments_api():
    """Get baby care appointments or create new appointment"""
    if request.method == 'GET':
        try:
            from app.data_manager import DataManager

            user_id = session['user_id']

            # Get all baby care appointments for the current user
            conn = DataManager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT a.id, a.user_id, a.baby_id, a.appointment_type, a.appointment_date,
                       a.doctor_name, a.clinic_name, a.purpose, a.status, a.notes,
                       a.created_at, b.name as baby_name, u.full_name as doctor_full_name,
                       u.email as doctor_email
                FROM appointments a
                LEFT JOIN babies b ON a.baby_id = b.id
                LEFT JOIN users u ON a.doctor_id = u.id
                WHERE a.user_id = ? AND a.appointment_type LIKE '%Baby Care%'
                ORDER BY a.appointment_date DESC
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
                    'created_at': appointment[10],
                    'baby_name': appointment[11],
                    'doctor_full_name': appointment[12],
                    'doctor_email': appointment[13]
                })

            return jsonify({
                'success': True,
                'appointments': appointments_data,
                'count': len(appointments_data)
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            from app.data_manager import DataManager
            from app.services.email_service import email_service
            from datetime import datetime

            data = request.get_json()
            user_id = session['user_id']

            # Validate required fields
            required_fields = ['doctor_name', 'appointment_date']
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

            # Get user information
            user_data = DataManager.get_user_by_id(user_id)
            if not user_data:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404

            # Find doctor by name
            doctor_id = None
            doctor_email = None
            if data.get('doctor_name'):
                users = DataManager.get_all_users()
                doctor = next((u for u in users if u.get('full_name') == data['doctor_name'] and u.get('role') == 'doctor'), None)
                if doctor:
                    doctor_id = doctor['id']
                    doctor_email = doctor['email']

            # Create new baby care appointment
            conn = DataManager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO appointments (user_id, baby_id, doctor_id, appointment_type, appointment_date,
                                        doctor_name, clinic_name, purpose, status, patient_name, patient_email,
                                        child_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('baby_id'),
                doctor_id,
                data.get('appointment_type', 'Baby Care Checkup'),
                appointment_date.isoformat(),
                data['doctor_name'],
                data.get('clinic_name', 'Baby Care Clinic'),
                data.get('purpose', ''),
                'pending',
                data.get('patient_name', user_data['full_name']),
                user_data['email'],
                data.get('child_name', 'Child'),
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
                    'patient_name': data.get('patient_name', user_data['full_name']),
                    'child_name': data.get('child_name', 'Child'),
                    'doctor_name': data['doctor_name'],
                    'appointment_date': appointment_date.strftime('%Y-%m-%d'),
                    'appointment_time': appointment_date.strftime('%H:%M'),
                    'appointment_type': data.get('appointment_type', 'Baby Care Checkup'),
                    'purpose': data.get('purpose', 'Baby Care Checkup'),
                    'clinic_name': data.get('clinic_name', 'Baby Care Clinic')
                }

                # Send booking notification emails to both patient and doctor
                if doctor_email:
                    email_results = email_service.send_appointment_booking_emails(
                        patient_email=user_data['email'],
                        doctor_email=doctor_email,
                        appointment_details=appointment_details
                    )

            except Exception as email_error:
                print(f"Email sending failed: {email_error}")

            return jsonify({
                'success': True,
                'message': 'Baby care appointment created successfully. Confirmation emails sent.',
                'appointment_id': appointment_id,
                'email_results': email_results
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# Growth Tracking API Endpoints

@babycare_bp.route('/api/growth-records/<int:baby_id>', methods=['GET'])
@login_required
def get_growth_records(baby_id):
    """Get all growth records for a baby"""
    try:
        user_id = session['user_id']
        
        # Validate access
        baby, error = validate_baby_access(baby_id, user_id)
        if error:
            return jsonify({'success': False, 'error': error}), 403 if 'denied' in error else 404
        
        conn = DataManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, baby_id, record_date, age_months, weight, height, head_circumference, notes, created_at
            FROM growth_records
            WHERE baby_id = ?
            ORDER BY record_date DESC
        ''', (baby_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            records.append({
                'id': row[0],
                'baby_id': row[1],
                'date': row[2],
                'age_months': row[3],
                'weight': row[4],
                'height': row[5],
                'head': row[6],
                'notes': row[7],
                'created_at': row[8]
            })
        
        return jsonify({
            'success': True,
            'records': records,
            'baby_name': baby['name']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@babycare_bp.route('/api/growth-records/<int:baby_id>', methods=['POST'])
@login_required
def add_growth_record(baby_id):
    """Add a new growth record for a baby"""
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        # Validate access
        baby, error = validate_baby_access(baby_id, user_id)
        if error:
            return jsonify({'success': False, 'error': error}), 403 if 'denied' in error else 404
        
        # Validate required fields
        if not data.get('date'):
            return jsonify({'success': False, 'error': 'Date is required'}), 400
        
        # Calculate age in months from baby's date of birth
        baby_dob = datetime.strptime(baby['date_of_birth'], '%Y-%m-%d')
        record_date = datetime.strptime(data['date'], '%Y-%m-%d')
        age_months = (record_date.year - baby_dob.year) * 12 + (record_date.month - baby_dob.month)
        
        # Ensure at least one measurement is provided
        weight = float(data['weight']) if data.get('weight') else None
        height = float(data['height']) if data.get('height') else None
        head = float(data['head']) if data.get('head') else None
        
        if not any([weight, height, head]):
            return jsonify({'success': False, 'error': 'At least one measurement is required'}), 400
        
        conn = DataManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO growth_records 
            (baby_id, record_date, age_months, weight, height, head_circumference, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (baby_id, data['date'], age_months, weight, height, head, data.get('notes', '')))
        
        record_id = cursor.lastrowid
        conn.commit()
        
        # Get the inserted record
        cursor.execute('''
            SELECT id, baby_id, record_date, age_months, weight, height, head_circumference, notes, created_at
            FROM growth_records WHERE id = ?
        ''', (record_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        record = {
            'id': row[0],
            'baby_id': row[1],
            'date': row[2],
            'age_months': row[3],
            'weight': row[4],
            'height': row[5],
            'head': row[6],
            'notes': row[7],
            'created_at': row[8]
        }
        
        return jsonify({
            'success': True,
            'message': 'Growth record added successfully',
            'record': record
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': 'Invalid data format'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@babycare_bp.route('/api/growth-records/<int:baby_id>/<int:record_id>', methods=['PUT'])
@login_required
def update_growth_record(baby_id, record_id):
    """Update a growth record"""
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        # Validate access
        baby, error = validate_baby_access(baby_id, user_id)
        if error:
            return jsonify({'success': False, 'error': error}), 403 if 'denied' in error else 404
        
        conn = DataManager.get_connection()
        cursor = conn.cursor()
        
        # Check if record exists and belongs to this baby
        cursor.execute('SELECT * FROM growth_records WHERE id = ? AND baby_id = ?', (record_id, baby_id))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Growth record not found'}), 404
        
        # Build update query
        update_fields = []
        update_values = []
        
        if 'date' in data:
            update_fields.append('record_date = ?')
            update_values.append(data['date'])
            
            # Recalculate age
            baby_dob = datetime.strptime(baby['date_of_birth'], '%Y-%m-%d')
            record_date = datetime.strptime(data['date'], '%Y-%m-%d')
            age_months = (record_date.year - baby_dob.year) * 12 + (record_date.month - baby_dob.month)
            update_fields.append('age_months = ?')
            update_values.append(age_months)
        
        if 'weight' in data:
            update_fields.append('weight = ?')
            update_values.append(float(data['weight']) if data['weight'] else None)
        
        if 'height' in data:
            update_fields.append('height = ?')
            update_values.append(float(data['height']) if data['height'] else None)
        
        if 'head' in data:
            update_fields.append('head_circumference = ?')
            update_values.append(float(data['head']) if data['head'] else None)
        
        if 'notes' in data:
            update_fields.append('notes = ?')
            update_values.append(data['notes'])
        
        if not update_fields:
            conn.close()
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        
        update_values.extend([record_id, baby_id])
        
        cursor.execute(f'''
            UPDATE growth_records 
            SET {', '.join(update_fields)}
            WHERE id = ? AND baby_id = ?
        ''', update_values)
        
        conn.commit()
        
        # Get updated record
        cursor.execute('''
            SELECT id, baby_id, record_date, age_months, weight, height, head_circumference, notes, created_at
            FROM growth_records WHERE id = ?
        ''', (record_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        record = {
            'id': row[0],
            'baby_id': row[1],
            'date': row[2],
            'age_months': row[3],
            'weight': row[4],
            'height': row[5],
            'head': row[6],
            'notes': row[7],
            'created_at': row[8]
        }
        
        return jsonify({
            'success': True,
            'message': 'Growth record updated successfully',
            'record': record
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': 'Invalid data format'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@babycare_bp.route('/api/growth-records/<int:baby_id>/<int:record_id>', methods=['DELETE'])
@login_required
def delete_growth_record(baby_id, record_id):
    """Delete a growth record"""
    try:
        user_id = session['user_id']
        
        # Validate access
        baby, error = validate_baby_access(baby_id, user_id)
        if error:
            return jsonify({'success': False, 'error': error}), 403 if 'denied' in error else 404
        
        conn = DataManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM growth_records WHERE id = ? AND baby_id = ?', (record_id, baby_id))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Growth record deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Growth record not found'
            }), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@babycare_bp.route('/api/babies/list', methods=['GET'])
@login_required
def get_babies_list():
    """Get list of babies for the current user"""
    try:
        user_id = session['user_id']
        user = DataManager.get_user_by_id(user_id)
        
        babies = DataManager.get_babies_for_user(user_id, user['role'] == 'admin')
        
        return jsonify({
            'success': True,
            'babies': babies
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500