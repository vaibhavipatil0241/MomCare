"""
Data Manager for Pregnancy Baby Care System
Handles all data operations using SQLite database
"""

import sqlite3
from datetime import datetime
from werkzeug.security import check_password_hash
from flask import current_app

class DataManager:
    @staticmethod
    def get_connection():
        """Get database connection"""
        return sqlite3.connect(current_app.config['DATABASE_PATH'])

    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, full_name, email, password_hash, role, phone, address,
                   date_of_birth, emergency_contact, is_active, created_at, last_login
            FROM users WHERE email = ? AND is_active = 1
        ''', (email,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'full_name': row[1],
                'email': row[2],
                'password_hash': row[3],
                'role': row[4],
                'phone': row[5],
                'address': row[6],
                'date_of_birth': row[7],
                'emergency_contact': row[8],
                'is_active': row[9],
                'created_at': row[10],
                'last_login': row[11]
            }
        return None

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, full_name, email, password_hash, role, phone, address,
                   date_of_birth, emergency_contact, is_active, created_at, last_login
            FROM users WHERE id = ? AND is_active = 1
        ''', (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'full_name': row[1],
                'email': row[2],
                'password_hash': row[3],
                'role': row[4],
                'phone': row[5],
                'address': row[6],
                'date_of_birth': row[7],
                'emergency_contact': row[8],
                'is_active': row[9],
                'created_at': row[10],
                'last_login': row[11]
            }
        return None

    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        user = DataManager.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            # Update last login
            conn = DataManager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user['id'],))
            conn.commit()
            conn.close()
            return user
        return None

    @staticmethod
    def create_user(user_data):
        """Create a new user"""
        from werkzeug.security import generate_password_hash

        conn = DataManager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (full_name, email, password_hash, role, phone, address,
                                 date_of_birth, emergency_contact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data.get('full_name'),
                user_data.get('email'),
                generate_password_hash(user_data.get('password')),
                user_data.get('role', 'user'),
                user_data.get('phone'),
                user_data.get('address'),
                user_data.get('date_of_birth'),
                user_data.get('emergency_contact')
            ))

            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return DataManager.get_user_by_id(user_id)
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def get_all_users():
        """Get all users"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, full_name, email, role, phone, is_active, created_at
            FROM users ORDER BY created_at DESC
        ''')

        rows = cursor.fetchall()
        conn.close()

        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'full_name': row[1],
                'email': row[2],
                'role': row[3],
                'phone': row[4],
                'is_active': row[5],
                'created_at': row[6]
            })

        return users

    @staticmethod
    def delete_user(user_id):
        """Delete a user permanently"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def soft_delete_user(user_id):
        """Soft delete a user (deactivate)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def get_babies_by_user(user_id):
        """Get all babies for a specific user"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, birth_date, gender, weight_at_birth, height_at_birth,
                   blood_type, unique_id, notes, created_at
            FROM babies WHERE parent_id = ? AND is_active = 1
            ORDER BY birth_date DESC
        ''', (user_id,))

        rows = cursor.fetchall()
        conn.close()

        babies = []
        for row in rows:
            babies.append({
                'id': row[0],
                'name': row[1],
                'birth_date': row[2],
                'gender': row[3],
                'weight_at_birth': row[4],
                'height_at_birth': row[5],
                'blood_type': row[6],
                'unique_id': row[7],
                'notes': row[8],
                'created_at': row[9]
            })

        return babies

    @staticmethod
    def get_baby_by_id(baby_id):
        """Get baby by ID"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, birth_date, gender, weight_at_birth, height_at_birth,
                   blood_type, parent_id, unique_id, notes, created_at
            FROM babies WHERE id = ? AND is_active = 1
        ''', (baby_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'name': row[1],
                'date_of_birth': row[2],  # For frontend compatibility
                'birth_date': row[2],      # Keep both for compatibility
                'gender': row[3],
                'weight_at_birth': row[4],
                'height_at_birth': row[5],
                'blood_type': row[6],
                'parent_id': row[7],
                'unique_id': row[8],
                'notes': row[9],
                'created_at': row[10]
            }
        return None

    @staticmethod
    def create_baby(baby_data):
        """Create a new baby record"""
        import uuid

        conn = DataManager.get_connection()
        cursor = conn.cursor()

        try:
            unique_id = DataManager.generate_enhanced_unique_id()

            cursor.execute('''
                INSERT INTO babies (name, birth_date, gender, weight_at_birth, height_at_birth,
                                  blood_type, parent_id, unique_id, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                baby_data.get('name'),
                baby_data.get('birth_date'),
                baby_data.get('gender'),
                baby_data.get('weight_at_birth'),
                baby_data.get('height_at_birth'),
                baby_data.get('blood_type'),
                baby_data.get('parent_id'),
                unique_id,
                baby_data.get('notes')
            ))

            baby_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return DataManager.get_baby_by_id(baby_id)
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    @staticmethod
    def get_babies_for_user(user_id, is_admin=False):
        """Get all babies for a specific user or all babies if admin"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        try:
            if is_admin:
                # Admin can see all babies
                cursor.execute('''
                    SELECT b.id, b.name, b.birth_date, b.gender, b.weight_at_birth, b.height_at_birth,
                           b.blood_type, b.parent_id, b.unique_id, b.notes, b.created_at,
                           u.full_name as parent_name, u.email as parent_email
                    FROM babies b
                    LEFT JOIN users u ON b.parent_id = u.id
                    WHERE b.is_active = 1
                    ORDER BY b.created_at DESC
                ''')
            else:
                # Regular user sees only their babies
                cursor.execute('''
                    SELECT b.id, b.name, b.birth_date, b.gender, b.weight_at_birth, b.height_at_birth,
                           b.blood_type, b.parent_id, b.unique_id, b.notes, b.created_at,
                           u.full_name as parent_name, u.email as parent_email
                    FROM babies b
                    LEFT JOIN users u ON b.parent_id = u.id
                    WHERE b.parent_id = ? AND b.is_active = 1
                    ORDER BY b.created_at DESC
                ''', (user_id,))

            rows = cursor.fetchall()
            conn.close()

            babies = []
            for row in rows:
                babies.append({
                    'id': row[0],
                    'name': row[1],
                    'date_of_birth': row[2],  # For frontend compatibility
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
                })

            return babies

        except Exception as e:
            conn.close()
            raise e

    @staticmethod
    def get_dashboard_stats():
        """Get comprehensive dashboard statistics"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        # Get various counts
        stats = {}

        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        stats['total_users'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM babies WHERE is_active = 1')
        stats['total_babies'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM vaccinations')
        stats['total_vaccinations'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM appointments')
        stats['total_appointments'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM growth_records')
        stats['total_growth_records'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM nutrition_records')
        stats['total_nutrition_records'] = cursor.fetchone()[0]



        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1")
        stats['admin_users'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor' AND is_active = 1")
        stats['doctor_users'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user' AND is_active = 1")
        stats['regular_users'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vaccinations WHERE status = 'completed'")
        stats['completed_vaccinations'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vaccinations WHERE status = 'scheduled'")
        stats['scheduled_vaccinations'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'scheduled'")
        stats['upcoming_appointments'] = cursor.fetchone()[0]

        conn.close()
        return stats

    @staticmethod
    def get_all_babies():
        """Return all babies (for admin views)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT b.id, b.name, b.birth_date, b.gender, b.weight_at_birth, b.height_at_birth,
                   b.blood_type, b.parent_id, b.unique_id, b.notes, b.created_at,
                   u.full_name as parent_name, u.email as parent_email
            FROM babies b
            LEFT JOIN users u ON b.parent_id = u.id
            WHERE b.is_active = 1
            ORDER BY b.created_at DESC
        ''')

        rows = cursor.fetchall()
        conn.close()

        babies = []
        for row in rows:
            babies.append({
                'id': row[0],
                'name': row[1],
                'birth_date': row[2],
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
            })

        return babies

    @staticmethod
    def get_all_vaccinations():
        """Return all vaccination records"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, baby_id, vaccine_name, scheduled_date, administered_date, status, doctor_name, created_at
            FROM vaccinations
            ORDER BY created_at DESC
        ''')

        rows = cursor.fetchall()
        conn.close()

        vaccs = []
        for row in rows:
            vaccs.append({
                'id': row[0],
                'baby_id': row[1],
                'vaccine_name': row[2],
                'scheduled_date': row[3],
                'administered_date': row[4],
                'status': row[5],
                'doctor_name': row[6],
                'created_at': row[7]
            })

        return vaccs

    @staticmethod
    def get_recent_appointments(limit=5):
        """Return recent appointment records (most recent first)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT a.id, a.user_id, a.baby_id, a.doctor_id, a.appointment_type, a.appointment_date, a.status, a.created_at,
                   u.full_name as user_name, d.full_name as doctor_name, b.name as baby_name
            FROM appointments a
            LEFT JOIN users u ON a.user_id = u.id
            LEFT JOIN users d ON a.doctor_id = d.id
            LEFT JOIN babies b ON a.baby_id = b.id
            ORDER BY a.created_at DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        appts = []
        for row in rows:
            appts.append({
                'id': row[0],
                'user_id': row[1],
                'baby_id': row[2],
                'doctor_id': row[3],
                'appointment_type': row[4],
                'appointment_date': row[5],
                'status': row[6],
                'created_at': row[7],
                'user_name': row[8],
                'doctor_name': row[9],
                'baby_name': row[10]
            })

        return appts

    @staticmethod
    def get_recent_unique_ids(limit=5):
        """Return recent unique ID creations (babies' unique IDs)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, unique_id, parent_id, created_at
            FROM babies
            WHERE unique_id IS NOT NULL
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        ids = []
        for row in rows:
            ids.append({
                'id': row[0],
                'name': row[1],
                'unique_id': row[2],
                'parent_id': row[3],
                'created_at': row[4]
            })

        return ids

    # Content Management Methods

    @staticmethod
    def get_all_nutrition_content():
        """Get all nutrition content"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, description, category, trimester, foods, tips,
                   is_active, created_at, updated_at
            FROM nutrition_content
            WHERE is_active = 1
            ORDER BY trimester, category, title
        ''')

        rows = cursor.fetchall()
        conn.close()

        nutrition_data = []
        for row in rows:
            import json
            nutrition_data.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'category': row[3],
                'trimester': row[4],
                'foods': json.loads(row[5]) if row[5] else [],
                'tips': row[6],
                'is_active': row[7],
                'created_at': row[8],
                'updated_at': row[9]
            })

        return nutrition_data

    @staticmethod
    def create_nutrition_content(title, description, category, trimester, foods, tips):
        """Create new nutrition content"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        import json
        cursor.execute('''
            INSERT INTO nutrition_content
            (title, description, category, trimester, foods, tips, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
        ''', (
            title,
            description,
            category,
            trimester,
            json.dumps(foods),
            tips,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        nutrition_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return nutrition_id

    @staticmethod
    def update_nutrition_content(nutrition_id, title, description, category, trimester, foods, tips):
        """Update nutrition content"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        import json
        cursor.execute('''
            UPDATE nutrition_content
            SET title = ?, description = ?, category = ?, trimester = ?,
                foods = ?, tips = ?, updated_at = ?
            WHERE id = ?
        ''', (
            title,
            description,
            category,
            trimester,
            json.dumps(foods),
            tips,
            datetime.now().isoformat(),
            nutrition_id
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def delete_nutrition_content(nutrition_id):
        """Delete nutrition content (soft delete)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE nutrition_content
            SET is_active = 0, updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), nutrition_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_all_vaccination_schedules():
        """Get all vaccination schedules"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, vaccine_name, age_months, description, side_effects, precautions,
                   is_active, created_at, updated_at
            FROM vaccination_schedules
            WHERE is_active = 1
            ORDER BY age_months, vaccine_name
        ''')

        rows = cursor.fetchall()
        conn.close()

        vaccination_data = []
        for row in rows:
            vaccination_data.append({
                'id': row[0],
                'vaccine_name': row[1],
                'age_months': row[2],
                'description': row[3],
                'side_effects': row[4],
                'precautions': row[5],
                'is_active': row[6],
                'created_at': row[7],
                'updated_at': row[8]
            })

        return vaccination_data

    @staticmethod
    def create_vaccination_schedule(vaccine_name, age_months, description, side_effects, precautions):
        """Create new vaccination schedule"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO vaccination_schedules
            (vaccine_name, age_months, description, side_effects, precautions, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        ''', (
            vaccine_name,
            age_months,
            description,
            side_effects,
            precautions,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        vaccination_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return vaccination_id

    @staticmethod
    def get_all_faqs():
        """Get all FAQs"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, question, answer, category, is_active, created_at, updated_at
            FROM faqs
            WHERE is_active = 1
            ORDER BY category, question
        ''')

        rows = cursor.fetchall()
        conn.close()

        faq_data = []
        for row in rows:
            faq_data.append({
                'id': row[0],
                'question': row[1],
                'answer': row[2],
                'category': row[3],
                'is_active': row[4],
                'created_at': row[5],
                'updated_at': row[6]
            })

        return faq_data

    @staticmethod
    def create_faq(question, answer, category):
        """Create new FAQ"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO faqs
            (question, answer, category, is_active, created_at, updated_at)
            VALUES (?, ?, ?, 1, ?, ?)
        ''', (
            question,
            answer,
            category,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        faq_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return faq_id

    @staticmethod
    def get_all_schemes():
        """Get all government schemes"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, description, eligibility, benefits, how_to_apply,
                   application_link, image_url, is_active, created_at, updated_at
            FROM government_schemes
            WHERE is_active = 1
            ORDER BY name
        ''')

        rows = cursor.fetchall()
        conn.close()

        schemes_data = []
        for row in rows:
            schemes_data.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'eligibility': row[3],
                'benefits': row[4],
                'how_to_apply': row[5],
                'application_link': row[6],
                'image_url': row[7],
                'is_active': row[8],
                'created_at': row[9],
                'updated_at': row[10]
            })

        return schemes_data

    # Unique ID Management Methods

    @staticmethod
    def get_baby_by_unique_id(unique_id):
        """Get baby by unique ID"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, birth_date, gender, weight_at_birth, height_at_birth,
                   blood_type, parent_id, unique_id, notes, created_at
            FROM babies WHERE unique_id = ? AND is_active = 1
        ''', (unique_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'name': row[1],
                'birth_date': row[2],
                'gender': row[3],
                'weight_at_birth': row[4],
                'height_at_birth': row[5],
                'blood_type': row[6],
                'parent_id': row[7],
                'unique_id': row[8],
                'notes': row[9],
                'created_at': row[10]
            }
        return None

    @staticmethod
    def validate_unique_id(unique_id):
        """Validate if unique ID exists and is active"""
        baby = DataManager.get_baby_by_unique_id(unique_id)
        return baby is not None

    @staticmethod
    def generate_enhanced_unique_id():
        """Generate an enhanced unique ID with better format"""
        import uuid
        import datetime

        # Format: BABY-YYYY-XXXXXXXX (e.g., BABY-2024-A1B2C3D4)
        year = datetime.datetime.now().year
        unique_part = uuid.uuid4().hex[:8].upper()
        return f"BABY-{year}-{unique_part}"

    @staticmethod
    def regenerate_baby_unique_id(baby_id, user_id):
        """Regenerate unique ID for a baby (with permission check)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        try:
            # First check if user has permission to modify this baby and get current ID
            cursor.execute('''
                SELECT parent_id, unique_id FROM babies WHERE id = ? AND is_active = 1
            ''', (baby_id,))

            result = cursor.fetchone()
            if not result:
                return None, "Baby not found"

            if result[0] != user_id:
                return None, "Access denied"

            old_unique_id = result[1]

            # Generate new unique ID
            new_unique_id = DataManager.generate_enhanced_unique_id()

            # Update the baby's unique ID
            cursor.execute('''
                UPDATE babies SET unique_id = ?, updated_at = ?
                WHERE id = ?
            ''', (new_unique_id, datetime.datetime.now().isoformat(), baby_id))

            conn.commit()
            conn.close()

            # Log the change to history
            DataManager.log_unique_id_change(baby_id, old_unique_id, new_unique_id, "User requested regeneration")

            return new_unique_id, None

        except Exception as e:
            conn.rollback()
            conn.close()
            return None, str(e)

    @staticmethod
    def get_baby_with_parent_info(unique_id):
        """Get baby information with parent details by unique ID"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT b.id, b.name, b.birth_date, b.gender, b.weight_at_birth,
                   b.height_at_birth, b.blood_type, b.unique_id, b.notes,
                   b.created_at, u.full_name as parent_name, u.email as parent_email,
                   u.phone as parent_phone
            FROM babies b
            JOIN users u ON b.parent_id = u.id
            WHERE b.unique_id = ? AND b.is_active = 1
        ''', (unique_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'name': row[1],
                'birth_date': row[2],
                'gender': row[3],
                'weight_at_birth': row[4],
                'height_at_birth': row[5],
                'blood_type': row[6],
                'unique_id': row[7],
                'notes': row[8],
                'created_at': row[9],
                'parent_name': row[10],
                'parent_email': row[11],
                'parent_phone': row[12]
            }
        return None

    @staticmethod
    def create_unique_id_history_table():
        """Create unique ID history table"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unique_id_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                baby_id INTEGER NOT NULL,
                old_unique_id TEXT NOT NULL,
                new_unique_id TEXT NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (baby_id) REFERENCES babies (id)
            )
        ''')

        conn.commit()
        conn.close()

    @staticmethod
    def log_unique_id_change(baby_id, old_unique_id, new_unique_id, reason="Manual regeneration"):
        """Log unique ID change to history"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO unique_id_history (baby_id, old_unique_id, new_unique_id, reason)
                VALUES (?, ?, ?, ?)
            ''', (baby_id, old_unique_id, new_unique_id, reason))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def get_unique_id_history(baby_id):
        """Get unique ID history for a baby"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT old_unique_id, new_unique_id, reason, created_at
            FROM unique_id_history
            WHERE baby_id = ?
            ORDER BY created_at DESC
        ''', (baby_id,))

        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append({
                'old_unique_id': row[0],
                'new_unique_id': row[1],
                'reason': row[2],
                'created_at': row[3]
            })

        return history

    @staticmethod
    def get_all_unique_ids_for_admin():
        """Get all unique IDs for admin management"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT b.id, b.name, b.birth_date, b.gender, b.unique_id, b.created_at,
                   u.full_name as parent_name, u.email as parent_email
            FROM babies b
            JOIN users u ON b.parent_id = u.id
            WHERE b.is_active = 1
            ORDER BY b.created_at DESC
        ''', ())

        rows = cursor.fetchall()
        conn.close()

        babies = []
        for row in rows:
            babies.append({
                'id': row[0],
                'name': row[1],
                'birth_date': row[2],
                'gender': row[3],
                'unique_id': row[4],
                'created_at': row[5],
                'parent_name': row[6],
                'parent_email': row[7]
            })

        return babies

    @staticmethod
    def create_scheme(name, description, eligibility, benefits, how_to_apply, application_link=None, image_url=None):
        """Create new government scheme"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO government_schemes
            (name, description, eligibility, benefits, how_to_apply, application_link, image_url, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        ''', (
            name,
            description,
            eligibility,
            benefits,
            how_to_apply,
            application_link,
            image_url,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        scheme_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return scheme_id

    # Exercise Management Methods

    @staticmethod
    def get_all_exercises():
        """Get all exercises"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, category, trimester, difficulty, duration, description,
                   instructions, precautions, benefits, equipment, video_url, image_url,
                   is_active, created_at, updated_at
            FROM exercises
            WHERE is_active = 1
            ORDER BY trimester, category, name
        ''')

        rows = cursor.fetchall()
        conn.close()

        exercises = []
        for row in rows:
            exercises.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'trimester': row[3],
                'difficulty': row[4],
                'duration': row[5],
                'description': row[6],
                'instructions': row[7],
                'precautions': row[8],
                'benefits': row[9],
                'equipment': row[10],
                'video_url': row[11],
                'image_url': row[12],
                'is_active': row[13],
                'created_at': row[14],
                'updated_at': row[15]
            })

        return exercises

    @staticmethod
    def create_exercise(name, category, trimester, difficulty, duration, description, instructions, precautions=None, benefits=None, equipment=None, video_url=None, image_url=None):
        """Create new exercise"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO exercises
            (name, category, trimester, difficulty, duration, description, instructions,
             precautions, benefits, equipment, video_url, image_url, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        ''', (
            name, category, trimester, difficulty, duration, description, instructions,
            precautions, benefits, equipment, video_url, image_url,
            datetime.now().isoformat(), datetime.now().isoformat()
        ))

        exercise_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return exercise_id

    @staticmethod
    def update_exercise(exercise_id, name, category, trimester, difficulty, duration, description, instructions, precautions=None, benefits=None, equipment=None, video_url=None, image_url=None):
        """Update exercise"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE exercises
            SET name = ?, category = ?, trimester = ?, difficulty = ?, duration = ?,
                description = ?, instructions = ?, precautions = ?, benefits = ?,
                equipment = ?, video_url = ?, image_url = ?, updated_at = ?
            WHERE id = ?
        ''', (
            name, category, trimester, difficulty, duration, description, instructions,
            precautions, benefits, equipment, video_url, image_url,
            datetime.now().isoformat(), exercise_id
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def delete_exercise(exercise_id):
        """Delete exercise (soft delete)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE exercises SET is_active = 0, updated_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), exercise_id))

        conn.commit()
        conn.close()

    @staticmethod
    def update_faq(faq_id, question, answer, category):
        """Update FAQ"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE faqs
            SET question = ?, answer = ?, category = ?, updated_at = ?
            WHERE id = ?
        ''', (
            question,
            answer,
            category,
            datetime.now().isoformat(),
            faq_id
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def delete_faq(faq_id):
        """Delete FAQ (soft delete)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE faqs
            SET is_active = 0, updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), faq_id))

        conn.commit()
        conn.close()

    @staticmethod
    def update_scheme(scheme_id, name, description, eligibility, benefits, how_to_apply, application_link=None, image_url=None):
        """Update government scheme"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE government_schemes
            SET name = ?, description = ?, eligibility = ?, benefits = ?,
                how_to_apply = ?, application_link = ?, image_url = ?, updated_at = ?
            WHERE id = ?
        ''', (
            name,
            description,
            eligibility,
            benefits,
            how_to_apply,
            application_link,
            image_url,
            datetime.now().isoformat(),
            scheme_id
        ))

        conn.commit()
        conn.close()

    # Meditation Management Methods

    @staticmethod
    def get_all_meditation_content():
        """Get all meditation content"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, description, trimester, duration, category, instructions,
                   benefits, audio_url, image_url, difficulty, is_active, created_at, updated_at
            FROM meditation_content
            WHERE is_active = 1
            ORDER BY trimester, category, title
        ''')

        rows = cursor.fetchall()
        conn.close()

        meditations = []
        for row in rows:
            meditations.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'trimester': row[3],
                'duration': row[4],
                'category': row[5],
                'instructions': row[6],
                'benefits': row[7],
                'audio_url': row[8],
                'image_url': row[9],
                'difficulty': row[10],
                'is_active': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            })

        return meditations

    @staticmethod
    def create_meditation_content(title, description, trimester, duration, category, instructions, benefits=None, audio_url=None, image_url=None, difficulty='beginner'):
        """Create new meditation content"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO meditation_content
            (title, description, trimester, duration, category, instructions, benefits,
             audio_url, image_url, difficulty, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        ''', (
            title, description, trimester, duration, category, instructions, benefits,
            audio_url, image_url, difficulty,
            datetime.now().isoformat(), datetime.now().isoformat()
        ))

        meditation_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return meditation_id

    @staticmethod
    def update_meditation_content(meditation_id, title, description, trimester, duration, category, instructions, benefits=None, audio_url=None, image_url=None, difficulty='beginner'):
        """Update meditation content"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE meditation_content
            SET title = ?, description = ?, trimester = ?, duration = ?, category = ?,
                instructions = ?, benefits = ?, audio_url = ?, image_url = ?, difficulty = ?, updated_at = ?
            WHERE id = ?
        ''', (
            title, description, trimester, duration, category, instructions, benefits,
            audio_url, image_url, difficulty, datetime.now().isoformat(), meditation_id
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def delete_meditation_content(meditation_id):
        """Delete meditation content (soft delete)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE meditation_content SET is_active = 0, updated_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), meditation_id))

        conn.commit()
        conn.close()

    # Wellness Tips Management Methods

    @staticmethod
    def get_all_wellness_tips():
        """Get all wellness tips"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, content, category, trimester, priority, is_active, created_at, updated_at
            FROM wellness_tips
            WHERE is_active = 1
            ORDER BY priority DESC, category, title
        ''')

        rows = cursor.fetchall()
        conn.close()

        tips = []
        for row in rows:
            tips.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'trimester': row[4],
                'priority': row[5],
                'is_active': row[6],
                'created_at': row[7],
                'updated_at': row[8]
            })

        return tips

    @staticmethod
    def create_wellness_tip(title, content, category, trimester=None, priority=1):
        """Create new wellness tip"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO wellness_tips
            (title, content, category, trimester, priority, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        ''', (
            title, content, category, trimester, priority,
            datetime.now().isoformat(), datetime.now().isoformat()
        ))

        tip_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return tip_id

    @staticmethod
    def update_wellness_tip(tip_id, title, content, category, trimester=None, priority=1):
        """Update wellness tip"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE wellness_tips
            SET title = ?, content = ?, category = ?, trimester = ?, priority = ?, updated_at = ?
            WHERE id = ?
        ''', (
            title, content, category, trimester, priority, datetime.now().isoformat(), tip_id
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def delete_wellness_tip(tip_id):
        """Delete wellness tip (soft delete)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE wellness_tips SET is_active = 0, updated_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), tip_id))

        conn.commit()
        conn.close()

    @staticmethod
    def delete_scheme(scheme_id):
        """Delete government scheme (soft delete)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE government_schemes
            SET is_active = 0, updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), scheme_id))

        conn.commit()
        conn.close()

    @staticmethod
    def update_vaccination_schedule(vaccination_id, vaccine_name, age_months, description, side_effects, precautions):
        """Update vaccination schedule"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE vaccination_schedules
            SET vaccine_name = ?, age_months = ?, description = ?,
                side_effects = ?, precautions = ?, updated_at = ?
            WHERE id = ?
        ''', (
            vaccine_name,
            age_months,
            description,
            side_effects,
            precautions,
            datetime.now().isoformat(),
            vaccination_id
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def delete_vaccination_schedule(vaccination_id):
        """Delete vaccination schedule (soft delete)"""
        conn = DataManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE vaccination_schedules
            SET is_active = 0, updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), vaccination_id))

        conn.commit()
        conn.close()