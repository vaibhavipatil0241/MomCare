from flask import Flask
import os
import sqlite3
from datetime import datetime

def create_app(config_name='development'):
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['DEBUG'] = True if config_name == 'development' else False

    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Use the existing instance directory for consistency
    instance_dir = os.path.join(os.path.dirname(basedir), 'instance')
    app.config['DATABASE_PATH'] = os.path.join(instance_dir, 'pregnancy_care.db')

    # Ensure instance folder exists
    try:
        os.makedirs(instance_dir)
    except OSError:
        pass

    # Initialize database
    init_database(app.config['DATABASE_PATH'])

    # Initialize email service
    from app.services.email_service import email_service
    email_service.init_app(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.doctor import doctor_bp
    from app.routes.demo import demo_bp
    from app.routes.pregnancy import pregnancy_bp
    from app.routes.babycare import babycare_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(demo_bp)
    app.register_blueprint(pregnancy_bp)
    app.register_blueprint(babycare_bp)
    app.register_blueprint(api_bp)

    return app

def add_content_management_tables(db_path):
    """Add content management tables to existing database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if medical_reports table exists first
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='medical_reports'")
    if cursor.fetchone() is None:
        print("🏗️  Adding medical_reports table...")
        cursor.execute('''
            CREATE TABLE medical_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                patient_name TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                report_type TEXT NOT NULL,
                report_date DATE NOT NULL,
                findings TEXT NOT NULL,
                recommendations TEXT,
                diagnosis TEXT,
                notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users (id),
                FOREIGN KEY (doctor_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
        print("✅ Medical reports table created successfully!")

    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nutrition_content'")
    if cursor.fetchone() is None:
        print("🏗️  Adding content management tables...")

        # Create content management tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrition_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                trimester TEXT NOT NULL,
                foods TEXT,
                tips TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vaccination_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vaccine_name TEXT NOT NULL,
                age_months INTEGER NOT NULL,
                description TEXT NOT NULL,
                side_effects TEXT,
                precautions TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS government_schemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                eligibility TEXT NOT NULL,
                benefits TEXT NOT NULL,
                how_to_apply TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                trimester TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                duration INTEGER,
                description TEXT NOT NULL,
                instructions TEXT NOT NULL,
                precautions TEXT,
                benefits TEXT,
                equipment TEXT,
                video_url TEXT,
                image_url TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meditation_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                trimester TEXT NOT NULL,
                duration INTEGER NOT NULL,
                category TEXT NOT NULL,
                instructions TEXT NOT NULL,
                benefits TEXT,
                audio_url TEXT,
                image_url TEXT,
                difficulty TEXT DEFAULT 'beginner',
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wellness_tips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                trimester TEXT,
                priority INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        conn.commit()
        print("✅ Content management tables added successfully!")
    else:
        print("✅ Content management tables already exist.")

    conn.close()

def update_database_schema(db_path):
    """Update existing database schema to ensure all required columns exist"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check appointments table schema
        cursor.execute("PRAGMA table_info(appointments)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]

        # Define required columns for appointments table
        required_columns = [
            ('patient_name', 'TEXT'),
            ('patient_email', 'TEXT'),
            ('child_name', 'TEXT'),
            ('reminder_sent', 'BOOLEAN DEFAULT 0'),
            ('confirmed_by_doctor', 'BOOLEAN DEFAULT 0'),
            ('completed_at', 'TIMESTAMP'),
            ('updated_at', 'TIMESTAMP')
        ]

        # Add missing columns
        for column_name, column_type in required_columns:
            if column_name not in existing_columns:
                try:
                    alter_sql = f"ALTER TABLE appointments ADD COLUMN {column_name} {column_type}"
                    cursor.execute(alter_sql)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"⚠️ Could not add column {column_name}: {e}")

        # Check growth_records table schema
        cursor.execute("PRAGMA table_info(growth_records)")
        growth_columns = cursor.fetchall()
        existing_growth_columns = [col[1] for col in growth_columns]

        # Add age_months column if it doesn't exist
        if 'age_months' not in existing_growth_columns:
            try:
                cursor.execute("ALTER TABLE growth_records ADD COLUMN age_months INTEGER")
                print(f"✅ Added column: age_months to growth_records")
            except sqlite3.Error as e:
                print(f"⚠️ Could not add column age_months: {e}")

        conn.commit()
        print("✅ Database schema updated successfully")

    except Exception as e:
        print(f"⚠️ Error updating database schema: {e}")
    finally:
        conn.close()

def init_database(db_path):
    """Initialize SQLite database with tables and sample data"""

    if os.path.exists(db_path):
        print("✅ Database already exists. Updating schema and checking tables...")
        # Update database schema to ensure all required columns exist
        update_database_schema(db_path)
        # Check if content management tables exist and create them if they don't
        add_content_management_tables(db_path)
        return

    print("🏗️  Creating SQLite database...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.executescript('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            phone TEXT,
            address TEXT,
            date_of_birth DATE,
            emergency_contact TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );

        CREATE TABLE babies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birth_date DATE NOT NULL,
            gender TEXT NOT NULL,
            weight_at_birth REAL,
            height_at_birth REAL,
            blood_type TEXT,
            parent_id INTEGER NOT NULL,
            unique_id TEXT UNIQUE NOT NULL,
            notes TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES users (id)
        );

        CREATE TABLE vaccinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            baby_id INTEGER NOT NULL,
            vaccine_name TEXT NOT NULL,
            scheduled_date DATE NOT NULL,
            administered_date DATE,
            status TEXT DEFAULT 'scheduled',
            doctor_name TEXT,
            clinic_name TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (baby_id) REFERENCES babies (id)
        );

        CREATE TABLE growth_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            baby_id INTEGER NOT NULL,
            record_date DATE NOT NULL,
            age_months INTEGER,
            weight REAL,
            height REAL,
            head_circumference REAL,
            doctor_name TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (baby_id) REFERENCES babies (id)
        );

        CREATE TABLE nutrition_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            baby_id INTEGER NOT NULL,
            record_date DATE NOT NULL,
            feeding_type TEXT NOT NULL,
            amount REAL,
            frequency INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (baby_id) REFERENCES babies (id)
        );



        CREATE TABLE appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            baby_id INTEGER,
            doctor_id INTEGER,
            appointment_type TEXT NOT NULL,
            appointment_date TIMESTAMP NOT NULL,
            doctor_name TEXT NOT NULL,
            clinic_name TEXT,
            purpose TEXT,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            patient_name TEXT,
            patient_email TEXT,
            child_name TEXT,
            reminder_sent BOOLEAN DEFAULT 0,
            confirmed_by_doctor BOOLEAN DEFAULT 0,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (baby_id) REFERENCES babies (id),
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        );

        CREATE TABLE medical_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            report_type TEXT NOT NULL,
            report_date DATE NOT NULL,
            findings TEXT NOT NULL,
            recommendations TEXT,
            diagnosis TEXT,
            notes TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users (id),
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        );
    ''')

    # No sample data - clean database for production use
    from werkzeug.security import generate_password_hash

    # Add content management tables using the helper function
    conn.close()  # Close current connection
    add_content_management_tables(db_path)

    # Reopen connection for final commit
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    conn.commit()
    conn.close()

    print("✅ SQLite database created with sample data!")