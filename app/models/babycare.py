from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
import uuid

# Import db from the main app module
from app import db

class Baby(db.Model):
    __tablename__ = 'babies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False, index=True)
    gender = db.Column(db.String(10), nullable=False)
    weight_at_birth = db.Column(db.Float, nullable=True)  # in kg
    height_at_birth = db.Column(db.Float, nullable=True)  # in cm
    blood_type = db.Column(db.String(5), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    unique_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    photo_url = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vaccinations = db.relationship('Vaccination', backref='baby', lazy=True, cascade='all, delete-orphan')
    growth_records = db.relationship('GrowthRecord', backref='baby', lazy=True, cascade='all, delete-orphan')
    nutrition_records = db.relationship('NutritionRecord', backref='baby', lazy=True, cascade='all, delete-orphan')

    appointments = db.relationship('Appointment', backref='baby', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Baby {self.name}>'

    def get_age_in_days(self):
        """Calculate age in days"""
        if self.birth_date:
            return (date.today() - self.birth_date).days
        return 0

    def get_age_in_months(self):
        """Calculate age in months"""
        return self.get_age_in_days() // 30

    def get_latest_growth_record(self):
        """Get the most recent growth record"""
        return GrowthRecord.query.filter_by(baby_id=self.id).order_by(GrowthRecord.record_date.desc()).first()

    def get_vaccination_progress(self):
        """Get vaccination progress statistics"""
        total_vaccinations = len(self.vaccinations)
        completed_vaccinations = len([v for v in self.vaccinations if v.status == 'completed'])
        return {
            'total': total_vaccinations,
            'completed': completed_vaccinations,
            'percentage': (completed_vaccinations / total_vaccinations * 100) if total_vaccinations > 0 else 0
        }

    def to_dict(self, include_relationships=False):
        data = {
            'id': self.id,
            'name': self.name,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'gender': self.gender,
            'weight_at_birth': self.weight_at_birth,
            'height_at_birth': self.height_at_birth,
            'blood_type': self.blood_type,
            'parent_id': self.parent_id,
            'unique_id': self.unique_id,
            'photo_url': self.photo_url,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'age_in_days': self.get_age_in_days(),
            'age_in_months': self.get_age_in_months(),
            'vaccination_progress': self.get_vaccination_progress()
        }

        if include_relationships:
            data.update({
                'parent_name': self.parent.full_name if self.parent else None,
                'parent_email': self.parent.email if self.parent else None,
                'vaccinations_count': len(self.vaccinations),
                'growth_records_count': len(self.growth_records),
                'nutrition_records_count': len(self.nutrition_records),

            })

        return data

    @staticmethod
    def generate_unique_id():
        """Generate a unique ID for baby"""
        import datetime
        year = datetime.datetime.now().year
        unique_part = uuid.uuid4().hex[:8].upper()
        return f"BABY-{year}-{unique_part}"

class Vaccination(db.Model):
    __tablename__ = 'vaccinations'

    id = db.Column(db.Integer, primary_key=True)
    baby_id = db.Column(db.Integer, db.ForeignKey('babies.id'), nullable=False, index=True)
    vaccine_name = db.Column(db.String(100), nullable=False)
    vaccine_type = db.Column(db.String(50), nullable=True)  # routine, optional, emergency
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    administered_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='scheduled', index=True)  # scheduled, completed, missed, postponed
    doctor_name = db.Column(db.String(100), nullable=True)
    clinic_name = db.Column(db.String(100), nullable=True)
    batch_number = db.Column(db.String(50), nullable=True)
    side_effects = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Vaccination {self.vaccine_name} for Baby {self.baby_id}>'

    def is_overdue(self):
        """Check if vaccination is overdue"""
        if self.status == 'scheduled' and self.scheduled_date < date.today():
            return True
        return False

    def days_until_due(self):
        """Calculate days until vaccination is due"""
        if self.scheduled_date:
            return (self.scheduled_date - date.today()).days
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'baby_id': self.baby_id,
            'vaccine_name': self.vaccine_name,
            'vaccine_type': self.vaccine_type,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'administered_date': self.administered_date.isoformat() if self.administered_date else None,
            'status': self.status,
            'doctor_name': self.doctor_name,
            'clinic_name': self.clinic_name,
            'batch_number': self.batch_number,
            'side_effects': self.side_effects,
            'notes': self.notes,
            'reminder_sent': self.reminder_sent,
            'is_overdue': self.is_overdue(),
            'days_until_due': self.days_until_due(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'baby_name': self.baby.name if self.baby else None
        }

class GrowthRecord(db.Model):
    __tablename__ = 'growth_records'

    id = db.Column(db.Integer, primary_key=True)
    baby_id = db.Column(db.Integer, db.ForeignKey('babies.id'), nullable=False, index=True)
    record_date = db.Column(db.Date, nullable=False, index=True)
    weight = db.Column(db.Float, nullable=True)  # in kg
    height = db.Column(db.Float, nullable=True)  # in cm
    head_circumference = db.Column(db.Float, nullable=True)  # in cm
    chest_circumference = db.Column(db.Float, nullable=True)  # in cm
    bmi = db.Column(db.Float, nullable=True)
    percentile_weight = db.Column(db.Float, nullable=True)
    percentile_height = db.Column(db.Float, nullable=True)
    doctor_name = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<GrowthRecord for Baby {self.baby_id} on {self.record_date}>'

    def calculate_bmi(self):
        """Calculate BMI if weight and height are available"""
        if self.weight and self.height:
            height_m = self.height / 100  # convert cm to meters
            return round(self.weight / (height_m ** 2), 2)
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'baby_id': self.baby_id,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'weight': self.weight,
            'height': self.height,
            'head_circumference': self.head_circumference,
            'chest_circumference': self.chest_circumference,
            'bmi': self.bmi or self.calculate_bmi(),
            'percentile_weight': self.percentile_weight,
            'percentile_height': self.percentile_height,
            'doctor_name': self.doctor_name,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'baby_name': self.baby.name if self.baby else None
        }

class NutritionRecord(db.Model):
    __tablename__ = 'nutrition_records'

    id = db.Column(db.Integer, primary_key=True)
    baby_id = db.Column(db.Integer, db.ForeignKey('babies.id'), nullable=False, index=True)
    record_date = db.Column(db.Date, nullable=False, index=True)
    feeding_type = db.Column(db.String(50), nullable=False)  # breastfeeding, formula, solid_food, mixed
    amount = db.Column(db.Float, nullable=True)  # in ml for liquids, grams for solids
    frequency = db.Column(db.Integer, nullable=True)  # times per day
    duration = db.Column(db.Integer, nullable=True)  # minutes for breastfeeding
    food_items = db.Column(db.Text, nullable=True)  # JSON string of food items
    allergic_reactions = db.Column(db.Text, nullable=True)
    appetite_level = db.Column(db.String(20), nullable=True)  # poor, fair, good, excellent
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<NutritionRecord for Baby {self.baby_id} on {self.record_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'baby_id': self.baby_id,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'feeding_type': self.feeding_type,
            'amount': self.amount,
            'frequency': self.frequency,
            'duration': self.duration,
            'food_items': self.food_items,
            'allergic_reactions': self.allergic_reactions,
            'appetite_level': self.appetite_level,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'baby_name': self.baby.name if self.baby else None
        }





