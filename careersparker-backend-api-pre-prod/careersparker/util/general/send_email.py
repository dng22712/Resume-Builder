import os

from django.utils.http import urlsafe_base64_encode
from jwt.utils import force_bytes
from rest_framework.response import Response

from templates.email.user.confirm_account_email import account_verification_email_template
from templates.email.user.forgot_password_email import forgot_password_email_template
from util.Permission.token_generator import TokenGenerator
from util.general.ses_send_email_config import send_email


# -----------------Send Forgot Password Email-----------------

def send_forgot_password_email(user, name, reset_account__url, temporary_password):
    """
    **Sends a forgotten password email to the specified user.**

    *Args:*

    - user (User): The user who requested a password reset.
    - name (str): The user's full name.
    - reset_account_url (str): The URL for resetting the user's password.
    - temporary_password (str): The temporary password to include in the email.

    Raises:

    - ValueError: If the user's email address is missing.
    """

    body_html = forgot_password_email_template()  # Todo: Update template html
    body_html = body_html.replace('fullname', name)
    body_html = body_html.replace('reset_account_email_url', reset_account__url)
    body_html = body_html.replace('temporary_password', temporary_password)
    email_subject = 'Reset your Career Sparker Account password'

    send_email(recipient=user.email, subject=email_subject, body_html=body_html)


# -----------------Send User Activation Email-----------------
def send_user_activation_email(request, user):
    """
    **Sends an account activation email to the specified user.**

    *Args:*

    - user (User): The user to activate.

    *Raises:*

    - ValueError: If the user's email address is missing.
    - Exception: If the email cannot be sent due to other errors.
    """
    name = user.first_name or user.last_name or user.username

    # Generate activation token
    token = TokenGenerator().make_token(user)
    uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
    user_activation_url = os.environ.get('USER_ACTIVATION_URL')
    verification_link = user_activation_url + '/verify-account/' + uid + '/' + token

    body_html = account_verification_email_template()  # Todo: Update template html
    body_html = body_html.replace('fullname', name)
    body_html = body_html.replace('confirm_email_url', verification_link)
    email_subject = 'Verify your email address and activate your account'

    try:
        send_email(recipient=user.email, subject=email_subject, body_html=body_html)
    except Exception as e:
        return Response({"error": "Email not sent", "Reason": str(e)}, status=400)
