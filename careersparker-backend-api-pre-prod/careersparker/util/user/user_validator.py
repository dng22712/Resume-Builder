import re


def validate_required_fields(email, username, first_name, last_name, password):
    """
    Validate required fields for user creation
        - user must have an email address
        - user must have a username
        - user must have a first name
        - user must have a last name
        - user must have a password
    """

    if not email:
        raise ValueError('Users must have an email address')
    if not username:
        raise ValueError('Users must have a username')
    if not first_name:
        raise ValueError('Users must have a first name')
    if not last_name:
        raise ValueError('Users must have a last name')
    if not password:
        raise ValueError('Users must have a password')


def validate_password_complexity(password, username, email, first_name, last_name):
    """
    Validate password complexity
        - password length
        - password uppercase
        - password lowercase
        - password number
        - password special character
        - password not contain username
        - password not contain email
        - password not contain first name
        - password not contain last name
    """

    if len(password) < 6:
        raise ValueError('Password must be at least 6 characters')
    if not re.search(r'[A-Z]', password):
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', password):
        raise ValueError('Password must contain at least one number')
    if not re.search(r'[^A-Za-z0-9]', password):
        raise ValueError('Password must contain at least one special character')
    if username in password:
        raise ValueError('Password must not contain username')
    if email.split('@')[0] in password:
        raise ValueError('Password must not contain email')
    if first_name in password:
        raise ValueError('Password must not contain first name')
    if last_name in password:
        raise ValueError('Password must not contain last name')


def validate_username(username):
    """
    Validate username
        - username not contain special characters
        - username not contain dots, "/" or spaces
        - username cannot contain uppercase letters
    """
    if not re.match("^[a-zA-Z0-9_]*$", username):
        raise ValueError('Username must not contain special characters')
    if '.' in username or ' ' in username or '/' in username:
        raise ValueError('Username must not contain dots, "/" or spaces')

    if not re.match("^[a-z0-9_]*$", username):
        raise ValueError('Username cannot contain uppercase letters')


def validate_new_password(password):
    """
    Validate new password
        - password length
        - password uppercase
        - password lowercase
        - password number
        - password special character
    """

    if len(password) < 6:
        raise ValueError('Password must be at least 6 characters')
    if not re.search(r'[A-Z]', password):
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', password):
        raise ValueError('Password must contain at least one number')
    if not re.search(r'[^A-Za-z0-9]', password):
        raise ValueError('Password must contain at least one special character')
