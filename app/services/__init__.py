"""
Services package for the Maternal and Child Health Care System
Contains service modules for email, notifications, and other business logic
"""

from .email_service import EmailService, email_service

__all__ = ['EmailService', 'email_service']
