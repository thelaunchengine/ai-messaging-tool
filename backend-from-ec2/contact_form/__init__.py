"""
Contact Form Automation Package
Handles automated contact form detection, submission, and monitoring
"""

from .form_detector import ContactFormDetector
from .form_submitter import ContactFormSubmitter
from .submission_tasks import (
    submit_contact_forms_task,
    retry_failed_submissions_task,
    monitor_submission_responses_task
)

__all__ = [
    'ContactFormDetector',
    'ContactFormSubmitter',
    'submit_contact_forms_task',
    'retry_failed_submissions_task',
    'monitor_submission_responses_task'
]

__version__ = '1.0.0'
__author__ = 'AI Messaging Tool Team'
