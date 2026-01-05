from datetime import datetime
from app import db

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    baby_id = db.Column(db.Integer, db.ForeignKey('babies.id'), nullable=True, index=True)
    appointment_type = db.Column(db.String(50), nullable=False)  # checkup, vaccination, consultation, emergency
    appointment_date = db.Column(db.DateTime, nullable=False, index=True)
    doctor_name = db.Column(db.String(100), nullable=False)
    clinic_name = db.Column(db.String(100), nullable=True)
    clinic_address = db.Column(db.Text, nullable=True)
    purpose = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='scheduled', index=True)  # scheduled, completed, cancelled, rescheduled
    notes = db.Column(db.Text, nullable=True)
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment {self.appointment_type} on {self.appointment_date}>'

    def is_upcoming(self):
        """Check if appointment is upcoming"""
        return self.appointment_date > datetime.utcnow() and self.status == 'scheduled'

    def is_overdue(self):
        """Check if appointment is overdue"""
        return self.appointment_date < datetime.utcnow() and self.status == 'scheduled'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'baby_id': self.baby_id,
            'appointment_type': self.appointment_type,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'doctor_name': self.doctor_name,
            'clinic_name': self.clinic_name,
            'clinic_address': self.clinic_address,
            'purpose': self.purpose,
            'status': self.status,
            'notes': self.notes,
            'reminder_sent': self.reminder_sent,
            'is_upcoming': self.is_upcoming(),
            'is_overdue': self.is_overdue(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_name': self.user.full_name if self.user else None,
            'baby_name': self.baby.name if self.baby else None
        }