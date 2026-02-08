"""
Email sender module using Sparkpost API.
"""
import time
from sparkpost import SparkPost


class EmailError(Exception):
    """Custom exception for email sending errors."""
    pass


def send_email(api_key, from_email, to_email, subject, html_content, max_retries=3):
    """
    Send an HTML email via Sparkpost API with retry logic.

    Args:
        api_key: Sparkpost API key
        from_email: Sender email address
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        max_retries: Maximum number of retry attempts (default: 3)

    Returns:
        True if email sent successfully

    Raises:
        EmailError: If email sending fails after all retries
    """
    sp = SparkPost(api_key)

    for attempt in range(max_retries):
        try:
            response = sp.transmissions.send(
                recipients=[to_email],
                html=html_content,
                from_email=from_email,
                subject=subject
            )

            # Check if email was accepted
            if response.get('total_accepted_recipients', 0) > 0:
                return True
            else:
                raise EmailError("Failed to send email: No recipients accepted")

        except Exception as e:
            # If this was the last attempt, raise EmailError
            if attempt == max_retries - 1:
                raise EmailError(f"Failed to send email after {max_retries} attempts: {str(e)}")

            # Exponential backoff: wait 2^attempt seconds
            wait_time = 2 ** attempt
            time.sleep(wait_time)

    # This should never be reached, but just in case
    raise EmailError("Failed to send email: Unknown error")
