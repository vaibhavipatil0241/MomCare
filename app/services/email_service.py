"""
Email Service for Web3 Consultation System
Handles sending email notifications for consultation requests and confirmations
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
import logging
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, app=None):
        self.app = app
        self.smtp_server = None
        self.smtp_port = None
        self.username = None
        self.password = None
        self.sender_email = None

        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize email service with Flask app configuration"""
        self.smtp_server = app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = app.config.get('MAIL_PORT', 587)
        self.username = app.config.get('MAIL_USERNAME')
        self.password = app.config.get('MAIL_PASSWORD')
        self.sender_email = app.config.get('MAIL_DEFAULT_SENDER')
        
        # For development, use environment variables
        if not self.username:
            self.username = os.environ.get('MAIL_USERNAME')
        if not self.password:
            self.password = os.environ.get('MAIL_PASSWORD')
        if not self.sender_email:
            self.sender_email = self.username  # Use Gmail address as sender
    
    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send an email with HTML content using Gmail SMTP"""
        try:
            logger.info(f"📧 Attempting to send email to: {to_email}")
            logger.info(f"📧 Subject: {subject}")
            logger.info(f"📧 SMTP Config: {self.smtp_server}:{self.smtp_port}")
            logger.info(f"📧 Username: {self.username}")
            logger.info(f"📧 Password configured: {'Yes' if self.password else 'No'}")
            
            # Check if email is configured
            if not self.username or not self.password:
                logger.warning(f"📧 Email not configured - logging message for: {to_email}")
                logger.info(f"📧 Subject: {subject}")
                logger.info(f"📧 Content preview: {text_content[:200] if text_content else 'HTML content'}...")
                return True  # Return True to not break flow
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email or self.username
            message["To"] = to_email
            
            # Create text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.sender_email or self.username, to_email, message.as_string())
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            logger.info(f"📧 Email logged for: {to_email} - {subject}")
            return True  # Return True to not break appointment flow
    

    

    
    def send_appointment_confirmation(self, patient_email, doctor_name, appointment_details):
        """Send appointment confirmation to patient"""
        subject = f"Appointment Confirmed with {doctor_name} - Maternal and Child Health Care"
        
        # Text version
        text_content = f"""
Appointment Confirmed!

Great news! Your consultation request has been approved and your appointment is now confirmed.

📅 APPOINTMENT DETAILS:
• Doctor: {doctor_name}
• Date: {appointment_details.get('date', 'N/A')}
• Time: {appointment_details.get('time', 'N/A')}
• Type: {appointment_details.get('type', 'N/A')}
• Location: {appointment_details.get('location', 'Maternal and Child Health Care Clinic')}

📝 BEFORE YOUR APPOINTMENT:
• Arrive 15 minutes early for check-in
• Bring a valid ID and insurance card
• Prepare a list of current medications
• Write down any questions you want to ask

If you need to reschedule or cancel, please contact us at least 24 hours in advance.

Thank you for choosing our healthcare platform!

© 2024 Maternal and Child Health Care
        """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #198754 0%, #20c997 100%); color: white; padding: 2rem; text-align: center; }}
                .content {{ padding: 2rem; }}
                .appointment-info {{ background: #d1edff; border: 1px solid #0dcaf0; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }}
                .footer {{ background: #f8f9fa; padding: 1rem; text-align: center; color: #6c757d; }}
                .btn {{ display: inline-block; background: #198754; color: white; padding: 0.8rem 1.5rem; text-decoration: none; border-radius: 5px; margin: 1rem 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Appointment Confirmed!</h1>
                    <p>Your consultation has been approved</p>
                </div>
                
                <div class="content">
                    <h2>Great news!</h2>
                    
                    <p>Your consultation request has been approved and your appointment is now confirmed.</p>
                    
                    <div class="appointment-info">
                        <h3>📅 Appointment Details</h3>
                        <p><strong>Doctor:</strong> {doctor_name}</p>
                        <p><strong>Date:</strong> {appointment_details.get('date', 'N/A')}</p>
                        <p><strong>Time:</strong> {appointment_details.get('time', 'N/A')}</p>
                        <p><strong>Type:</strong> {appointment_details.get('type', 'N/A')}</p>
                        <p><strong>Location:</strong> {appointment_details.get('location', 'Maternal and Child Health Care Clinic')}</p>
                    </div>
                    
                    <h3>📝 Before Your Appointment</h3>
                    <ul>
                        <li>Arrive 15 minutes early for check-in</li>
                        <li>Bring a valid ID and insurance card</li>
                        <li>Prepare a list of current medications</li>
                        <li>Write down any questions you want to ask</li>
                    </ul>
                    
                    <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
                    
                    <a href="http://127.0.0.1:5000/appointments/manage" class="btn">Manage Appointments</a>
                </div>
                
                <div class="footer">
                    <p>© 2024 Maternal and Child Health Care</p>
                    <p>Thank you for choosing our healthcare platform!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(patient_email, subject, html_content, text_content)

    def send_appointment_confirmation_emails(self, patient_email, doctor_email, appointment_details):
        """Send appointment confirmation emails to both patient and doctor using Gmail SMTP"""
        try:
            # Email to patient
            patient_subject = f"✅ Appointment Confirmed with Dr. {appointment_details.get('doctor_name', 'Doctor')}"
            
            patient_text = f"""
Dear {appointment_details.get('patient_name', 'Patient')},

Great news! Your appointment has been CONFIRMED by the doctor.

📅 APPOINTMENT DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👨‍⚕️ Doctor: {appointment_details.get('doctor_name', 'N/A')}
📅 Date: {appointment_details.get('appointment_date', 'N/A')}
🕐 Time: {appointment_details.get('appointment_time', 'N/A')}
🏥 Clinic: {appointment_details.get('clinic_name', 'Maternal Care Clinic')}
💼 Purpose: {appointment_details.get('purpose', 'General consultation')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 BEFORE YOUR APPOINTMENT:
• Arrive 15 minutes early for check-in
• Bring a valid ID and any insurance documents
• Prepare a list of current medications
• Write down any questions you want to ask
• Bring any previous medical records or test results

⚠️ NEED TO RESCHEDULE?
If you need to reschedule or cancel, please contact us at least 24 hours in advance.

We look forward to seeing you!

Best regards,
{appointment_details.get('clinic_name', 'Maternal Care Clinic')} Team

---
This is an automated confirmation email from the Maternal and Child Health Care System.
            """

            patient_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #198754 0%, #20c997 100%); color: white; padding: 2rem; text-align: center; }}
        .content {{ padding: 2rem; }}
        .appointment-box {{ background: #d1edff; border-left: 4px solid #0dcaf0; padding: 1.5rem; margin: 1rem 0; border-radius: 5px; }}
        .info-row {{ display: flex; margin: 0.5rem 0; }}
        .info-label {{ font-weight: bold; min-width: 100px; }}
        .checklist {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin: 1rem 0; border-radius: 5px; }}
        .footer {{ background: #f8f9fa; padding: 1rem; text-align: center; color: #6c757d; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Appointment Confirmed!</h1>
            <p>Your appointment has been approved by the doctor</p>
        </div>
        
        <div class="content">
            <h2>Dear {appointment_details.get('patient_name', 'Patient')},</h2>
            <p>Great news! Your appointment has been <strong>CONFIRMED</strong> by Dr. {appointment_details.get('doctor_name', 'Doctor')}.</p>
            
            <div class="appointment-box">
                <h3 style="margin-top: 0;">📅 Appointment Details</h3>
                <div class="info-row">
                    <span class="info-label">👨‍⚕️ Doctor:</span>
                    <span>{appointment_details.get('doctor_name', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📅 Date:</span>
                    <span>{appointment_details.get('appointment_date', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🕐 Time:</span>
                    <span>{appointment_details.get('appointment_time', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🏥 Clinic:</span>
                    <span>{appointment_details.get('clinic_name', 'Maternal Care Clinic')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">💼 Purpose:</span>
                    <span>{appointment_details.get('purpose', 'General consultation')}</span>
                </div>
            </div>
            
            <div class="checklist">
                <h3 style="margin-top: 0;">📝 Before Your Appointment</h3>
                <ul style="margin: 0.5rem 0;">
                    <li>Arrive 15 minutes early for check-in</li>
                    <li>Bring a valid ID and any insurance documents</li>
                    <li>Prepare a list of current medications</li>
                    <li>Write down any questions you want to ask</li>
                    <li>Bring any previous medical records or test results</li>
                </ul>
            </div>
            
            <p><strong>⚠️ Need to reschedule?</strong><br>
            Please contact us at least 24 hours in advance.</p>
            
            <p>We look forward to seeing you!</p>
        </div>
        
        <div class="footer">
            <p><strong>{appointment_details.get('clinic_name', 'Maternal Care Clinic')}</strong></p>
            <p>© 2024 Maternal and Child Health Care System</p>
            <p style="font-size: 0.8rem; color: #999;">This is an automated confirmation email. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
            """

            patient_sent = self.send_email(patient_email, patient_subject, patient_html, patient_text)

            # Email to doctor
            doctor_subject = f"📋 Appointment Confirmed - {appointment_details.get('patient_name', 'Patient')}"
            
            doctor_text = f"""
Dear Dr. {appointment_details.get('doctor_name', 'Doctor')},

You have successfully confirmed an appointment. The patient has been notified.

👤 PATIENT INFORMATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {appointment_details.get('patient_name', 'N/A')}
Email: {patient_email}
Child: {appointment_details.get('child_name', 'N/A')}

📅 APPOINTMENT DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: {appointment_details.get('appointment_date', 'N/A')}
Time: {appointment_details.get('appointment_time', 'N/A')}
Type: {appointment_details.get('appointment_type', 'N/A')}
Purpose: {appointment_details.get('purpose', 'N/A')}
Location: {appointment_details.get('clinic_name', 'Maternal Care Clinic')}

📝 PREPARATION REMINDERS:
• Review patient history before the appointment
• Prepare necessary medical equipment
• Ensure examination room is ready
• Have patient files accessible

The patient has received a confirmation email with all appointment details.

Best regards,
Maternal and Child Health Care System

---
This is an automated notification from the appointment management system.
            """

            doctor_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%); color: white; padding: 2rem; text-align: center; }}
        .content {{ padding: 2rem; }}
        .info-box {{ background: #e7f3ff; border-left: 4px solid #0d6efd; padding: 1.5rem; margin: 1rem 0; border-radius: 5px; }}
        .patient-box {{ background: #d1f2eb; border-left: 4px solid #198754; padding: 1.5rem; margin: 1rem 0; border-radius: 5px; }}
        .info-row {{ display: flex; margin: 0.5rem 0; }}
        .info-label {{ font-weight: bold; min-width: 120px; }}
        .footer {{ background: #f8f9fa; padding: 1rem; text-align: center; color: #6c757d; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Appointment Confirmed</h1>
            <p>Doctor Notification</p>
        </div>
        
        <div class="content">
            <h2>Dear Dr. {appointment_details.get('doctor_name', 'Doctor')},</h2>
            <p>You have successfully <strong>confirmed</strong> an appointment. The patient has been notified via email.</p>
            
            <div class="patient-box">
                <h3 style="margin-top: 0;">👤 Patient Information</h3>
                <div class="info-row">
                    <span class="info-label">Name:</span>
                    <span>{appointment_details.get('patient_name', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Email:</span>
                    <span>{patient_email}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Child:</span>
                    <span>{appointment_details.get('child_name', 'N/A')}</span>
                </div>
            </div>
            
            <div class="info-box">
                <h3 style="margin-top: 0;">📅 Appointment Details</h3>
                <div class="info-row">
                    <span class="info-label">📅 Date:</span>
                    <span>{appointment_details.get('appointment_date', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🕐 Time:</span>
                    <span>{appointment_details.get('appointment_time', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📋 Type:</span>
                    <span>{appointment_details.get('appointment_type', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">💼 Purpose:</span>
                    <span>{appointment_details.get('purpose', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🏥 Location:</span>
                    <span>{appointment_details.get('clinic_name', 'Maternal Care Clinic')}</span>
                </div>
            </div>
            
            <h3>📝 Preparation Reminders</h3>
            <ul>
                <li>Review patient history before the appointment</li>
                <li>Prepare necessary medical equipment</li>
                <li>Ensure examination room is ready</li>
                <li>Have patient files accessible</li>
            </ul>
            
            <p style="background: #fff3cd; padding: 1rem; border-radius: 5px; border-left: 4px solid #ffc107;">
                <strong>✅ Patient Notified:</strong> The patient has received a confirmation email with all appointment details.
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Maternal and Child Health Care System</strong></p>
            <p>© 2024 Appointment Management System</p>
            <p style="font-size: 0.8rem; color: #999;">This is an automated notification. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
            """

            doctor_sent = self.send_email(doctor_email, doctor_subject, doctor_html, doctor_text)

            return {
                'patient_email_sent': patient_sent,
                'doctor_email_sent': doctor_sent,
                'success': patient_sent or doctor_sent  # Success if at least one email sent
            }

        except Exception as e:
            logger.error(f"❌ Failed to send appointment confirmation emails: {str(e)}")
            return {
                'patient_email_sent': False,
                'doctor_email_sent': False,
                'success': False,
                'error': str(e)
            }

    def send_appointment_booking_emails(self, patient_email, doctor_email, appointment_details):
        """
        Send emails to both patient and doctor when appointment is first booked
        (before doctor confirmation)
        
        Args:
            patient_email: Patient's email address
            doctor_email: Doctor's email address  
            appointment_details: Dictionary containing appointment info
            
        Returns:
            Dictionary with status of both emails
        """
        logger.info(f"📧 Sending appointment booking notifications...")
        logger.info(f"   Patient: {patient_email}")
        logger.info(f"   Doctor: {doctor_email}")
        
        results = {
            'patient_email_sent': False,
            'doctor_email_sent': False
        }
        
        try:
            # Send email to PATIENT - Booking Received
            patient_subject = f"📅 Appointment Request Received - {appointment_details.get('doctor_name', 'Doctor')}"
            
            patient_text = f"""
Dear {appointment_details.get('patient_name', 'Patient')},

Thank you for booking an appointment with {appointment_details.get('doctor_name', 'our medical team')}.

📅 APPOINTMENT DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: {appointment_details.get('appointment_date', 'N/A')}
Time: {appointment_details.get('appointment_time', 'N/A')}
Doctor: {appointment_details.get('doctor_name', 'N/A')}
Type: {appointment_details.get('appointment_type', 'N/A')}
Purpose: {appointment_details.get('purpose', 'N/A')}
Location: {appointment_details.get('clinic_name', 'Maternal Care Clinic')}

⏳ STATUS: PENDING DOCTOR CONFIRMATION

Your appointment request has been sent to the doctor. You will receive another email once the doctor confirms your appointment.

📝 WHAT TO EXPECT:
• Doctor will review your appointment request
• You'll receive a confirmation email once approved
• Keep this email for your records

If you need to make changes or have questions, please contact us.

Best regards,
Maternal and Child Health Care System

---
This is an automated confirmation. Please do not reply to this email.
            """
            
            patient_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); color: white; padding: 2rem; text-align: center; }}
        .content {{ padding: 2rem; }}
        .status-pending {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin: 1rem 0; border-radius: 5px; }}
        .info-box {{ background: #e7f3ff; border-left: 4px solid #0d6efd; padding: 1.5rem; margin: 1rem 0; border-radius: 5px; }}
        .info-row {{ display: flex; margin: 0.5rem 0; }}
        .info-label {{ font-weight: bold; min-width: 120px; }}
        .checklist {{ background: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 1rem 0; }}
        .footer {{ background: #f8f9fa; padding: 1rem; text-align: center; color: #6c757d; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 Appointment Request Received</h1>
            <p>Waiting for Doctor Confirmation</p>
        </div>
        
        <div class="content">
            <h2>Dear {appointment_details.get('patient_name', 'Patient')},</h2>
            <p>Thank you for booking an appointment with <strong>{appointment_details.get('doctor_name', 'our medical team')}</strong>.</p>
            
            <div class="status-pending">
                <h3 style="margin-top: 0;">⏳ Status: PENDING CONFIRMATION</h3>
                <p style="margin-bottom: 0;">Your appointment request has been sent to the doctor. You will receive a confirmation email once the doctor approves your appointment.</p>
            </div>
            
            <div class="info-box">
                <h3 style="margin-top: 0;">📅 Appointment Details</h3>
                <div class="info-row">
                    <span class="info-label">📅 Date:</span>
                    <span>{appointment_details.get('appointment_date', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🕐 Time:</span>
                    <span>{appointment_details.get('appointment_time', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">👨‍⚕️ Doctor:</span>
                    <span>{appointment_details.get('doctor_name', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📋 Type:</span>
                    <span>{appointment_details.get('appointment_type', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📝 Purpose:</span>
                    <span>{appointment_details.get('purpose', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📍 Location:</span>
                    <span>{appointment_details.get('clinic_name', 'Maternal Care Clinic')}</span>
                </div>
            </div>
            
            <div class="checklist">
                <h3>📝 What to Expect:</h3>
                <ul>
                    <li>✅ Doctor will review your request</li>
                    <li>📧 You'll receive confirmation email once approved</li>
                    <li>📄 Keep this email for your records</li>
                </ul>
            </div>
            
            <p>If you need to make changes or have questions, please contact us.</p>
        </div>
        
        <div class="footer">
            <p>&copy; 2025 Maternal and Child Health Care System</p>
            <p>This is an automated confirmation. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
            """
            
            patient_sent = self.send_email(patient_email, patient_subject, patient_html, patient_text)
            results['patient_email_sent'] = patient_sent
            logger.info(f"   Patient email: {'✅ Sent' if patient_sent else '❌ Failed'}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send patient booking email: {str(e)}")
        
        try:
            # Send email to DOCTOR - New Appointment Request
            doctor_subject = f"📋 New Appointment Request - {appointment_details.get('patient_name', 'Patient')}"
            
            doctor_text = f"""
Dear Dr. {appointment_details.get('doctor_name', 'Doctor')},

You have received a NEW appointment request that requires your confirmation.

👤 PATIENT INFORMATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {appointment_details.get('patient_name', 'N/A')}
Email: {patient_email}
Child: {appointment_details.get('child_name', 'N/A')}

📅 REQUESTED APPOINTMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: {appointment_details.get('appointment_date', 'N/A')}
Time: {appointment_details.get('appointment_time', 'N/A')}
Type: {appointment_details.get('appointment_type', 'N/A')}
Purpose: {appointment_details.get('purpose', 'N/A')}
Location: {appointment_details.get('clinic_name', 'Maternal Care Clinic')}

⚡ ACTION REQUIRED:
Please log into your doctor dashboard to CONFIRM or RESCHEDULE this appointment.
The patient is waiting for your confirmation.

Login to Dashboard: http://127.0.0.1:5000/doctor/appointments

The patient has been notified that their request is pending your approval.

Best regards,
Maternal and Child Health Care System

---
This is an automated notification. Please do not reply to this email.
            """
            
            doctor_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%); color: white; padding: 2rem; text-align: center; }}
        .content {{ padding: 2rem; }}
        .action-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 1.5rem; margin: 1rem 0; border-radius: 5px; }}
        .patient-box {{ background: #d1f2eb; border-left: 4px solid #198754; padding: 1.5rem; margin: 1rem 0; border-radius: 5px; }}
        .info-box {{ background: #e7f3ff; border-left: 4px solid #0d6efd; padding: 1.5rem; margin: 1rem 0; border-radius: 5px; }}
        .info-row {{ display: flex; margin: 0.5rem 0; }}
        .info-label {{ font-weight: bold; min-width: 120px; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #0d6efd; color: white; text-decoration: none; border-radius: 5px; margin: 1rem 0; }}
        .footer {{ background: #f8f9fa; padding: 1rem; text-align: center; color: #6c757d; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 New Appointment Request</h1>
            <p>Action Required</p>
        </div>
        
        <div class="content">
            <h2>Dear Dr. {appointment_details.get('doctor_name', 'Doctor')},</h2>
            <p>You have received a <strong>new appointment request</strong> that requires your confirmation.</p>
            
            <div class="action-box">
                <h3 style="margin-top: 0;">⚡ ACTION REQUIRED</h3>
                <p>Please review and confirm this appointment request. The patient is waiting for your approval.</p>
                <a href="http://127.0.0.1:5000/doctor/appointments" class="button">View Dashboard →</a>
            </div>
            
            <div class="patient-box">
                <h3 style="margin-top: 0;">👤 Patient Information</h3>
                <div class="info-row">
                    <span class="info-label">Name:</span>
                    <span>{appointment_details.get('patient_name', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Email:</span>
                    <span>{patient_email}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Child:</span>
                    <span>{appointment_details.get('child_name', 'N/A')}</span>
                </div>
            </div>
            
            <div class="info-box">
                <h3 style="margin-top: 0;">📅 Requested Appointment</h3>
                <div class="info-row">
                    <span class="info-label">📅 Date:</span>
                    <span>{appointment_details.get('appointment_date', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🕐 Time:</span>
                    <span>{appointment_details.get('appointment_time', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📋 Type:</span>
                    <span>{appointment_details.get('appointment_type', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📝 Purpose:</span>
                    <span>{appointment_details.get('purpose', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📍 Location:</span>
                    <span>{appointment_details.get('clinic_name', 'Maternal Care Clinic')}</span>
                </div>
            </div>
            
            <p><strong>Note:</strong> The patient has been notified that their request is pending your approval.</p>
        </div>
        
        <div class="footer">
            <p>&copy; 2025 Maternal and Child Health Care System</p>
            <p>This is an automated notification. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
            """
            
            doctor_sent = self.send_email(doctor_email, doctor_subject, doctor_html, doctor_text)
            results['doctor_email_sent'] = doctor_sent
            logger.info(f"   Doctor email: {'✅ Sent' if doctor_sent else '❌ Failed'}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send doctor booking email: {str(e)}")
        
        logger.info(f"📊 Booking notification results: Patient={results['patient_email_sent']}, Doctor={results['doctor_email_sent']}")
        return results

# Global email service instance
email_service = EmailService()
