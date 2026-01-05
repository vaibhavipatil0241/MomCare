from datetime import datetime
from app import db

class WeightEntry(db.Model):
    """Model for tracking pregnancy weight entries"""
    __tablename__ = 'weight_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow, index=True)
    weight = db.Column(db.Float, nullable=False)  # Current weight in kg
    pregnancy_week = db.Column(db.Integer, nullable=False)  # Week of pregnancy (4-40)
    pre_pregnancy_weight = db.Column(db.Float, nullable=True)  # Pre-pregnancy weight in kg
    height = db.Column(db.Float, nullable=True)  # Height in cm
    bmi = db.Column(db.Float, nullable=True)  # Calculated BMI
    weight_gain = db.Column(db.Float, nullable=True)  # Total weight gain since pre-pregnancy
    notes = db.Column(db.Text, nullable=True)  # Optional notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref=db.backref('weight_entries', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<WeightEntry user_id={self.user_id} week={self.pregnancy_week} weight={self.weight}kg>'

    def calculate_bmi(self):
        """Calculate BMI from pre-pregnancy weight and height"""
        if self.pre_pregnancy_weight and self.height:
            height_m = self.height / 100
            self.bmi = round(self.pre_pregnancy_weight / (height_m * height_m), 1)
            return self.bmi
        return None

    def calculate_weight_gain(self):
        """Calculate total weight gain"""
        if self.pre_pregnancy_weight:
            self.weight_gain = round(self.weight - self.pre_pregnancy_weight, 1)
            return self.weight_gain
        return None

    def get_bmi_category(self):
        """Get BMI category"""
        if not self.bmi:
            return 'unknown'
        if self.bmi < 18.5:
            return 'underweight'
        elif self.bmi < 25:
            return 'normal'
        elif self.bmi < 30:
            return 'overweight'
        else:
            return 'obese'

    def get_recommended_gain_range(self):
        """Get recommended weight gain range based on BMI category"""
        category = self.get_bmi_category()
        ranges = {
            'underweight': {'total': '12.7-18.1 kg', 'weekly': '0.44-0.58 kg/week'},
            'normal': {'total': '11.3-15.9 kg', 'weekly': '0.35-0.50 kg/week'},
            'overweight': {'total': '6.8-11.3 kg', 'weekly': '0.23-0.33 kg/week'},
            'obese': {'total': '5.0-9.1 kg', 'weekly': '0.17-0.27 kg/week'}
        }
        return ranges.get(category, {'total': 'N/A', 'weekly': 'N/A'})

    def get_status(self):
        """Determine if weight gain is on track, low, or high"""
        if not self.weight_gain or not self.bmi:
            return 'unknown'

        category = self.get_bmi_category()
        week = self.pregnancy_week

        # First trimester (weeks 1-13)
        if week <= 13:
            if self.weight_gain < 0.5:
                return 'low'
            elif self.weight_gain > 2.0:
                return 'high'
            else:
                return 'good'

        # Second and third trimester (weeks 14-40)
        weeks_since_first_trimester = week - 13

        # Expected gain based on BMI category
        if category == 'underweight':
            expected_min = 0.5 + (weeks_since_first_trimester * 0.44)
            expected_max = 2.0 + (weeks_since_first_trimester * 0.58)
        elif category == 'normal':
            expected_min = 0.5 + (weeks_since_first_trimester * 0.35)
            expected_max = 2.0 + (weeks_since_first_trimester * 0.50)
        elif category == 'overweight':
            expected_min = 0.5 + (weeks_since_first_trimester * 0.23)
            expected_max = 2.0 + (weeks_since_first_trimester * 0.33)
        else:  # obese
            expected_min = 0.5 + (weeks_since_first_trimester * 0.17)
            expected_max = 2.0 + (weeks_since_first_trimester * 0.27)

        if self.weight_gain < expected_min:
            return 'low'
        elif self.weight_gain > expected_max:
            return 'high'
        else:
            return 'good'

    def to_dict(self):
        """Convert weight entry to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'weight': self.weight,
            'pregnancy_week': self.pregnancy_week,
            'pre_pregnancy_weight': self.pre_pregnancy_weight,
            'height': self.height,
            'bmi': self.bmi,
            'bmi_category': self.get_bmi_category(),
            'weight_gain': self.weight_gain,
            'status': self.get_status(),
            'recommended_gain': self.get_recommended_gain_range(),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def get_by_user(user_id, limit=None):
        """Get all weight entries for a user, ordered by pregnancy week"""
        query = WeightEntry.query.filter_by(user_id=user_id).order_by(WeightEntry.pregnancy_week.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_latest(user_id):
        """Get the latest weight entry for a user"""
        return WeightEntry.query.filter_by(user_id=user_id).order_by(WeightEntry.pregnancy_week.desc()).first()

    @staticmethod
    def delete_entry(entry_id, user_id):
        """Delete a weight entry (with user validation)"""
        entry = WeightEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return True
        return False
