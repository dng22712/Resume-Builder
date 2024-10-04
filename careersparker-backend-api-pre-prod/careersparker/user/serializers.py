import string

from django.contrib.auth import get_user_model, authenticate, password_validation
from rest_framework import serializers
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from util.signal_notifier.signal import create_user_profile
from util.user.user_validator import validate_required_fields, validate_password_complexity, validate_username


class UserSerializer(serializers.ModelSerializer):
    """
     Serializer for the User model.

    This serializer handles the serialization and deserialization of User objects.
    It includes custom methods for creating, updating, and validating user data.

    Attributes:
    Meta:
            model (class): The User model to be serialized.
            fields (str or tuple): Specifies the fields to be included in the serialization.
            extra_kwargs (dict): Additional keyword arguments for customizing field behavior.

    Methods:
        create(validated_data):
            Create a new user instance using the provided validated data.

        update(instance, validated_data):
            Update an existing user instance with the provided validated data.

        validate(data):
            Validate the incoming user data, checking for unique email and username.

    Example:
        serializer = UserSerializer(data=request_data)
        if serializer.is_valid():
            serializer.save()

    """

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'password',
            'first_name',
            'last_name',
            'username',
            'is_staff',
            'is_verified',
            'is_active',
            'role',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 6}}

    def create(self, validated_data):
        """
        Create a new user instance.

        Args:
            validated_data (dict): Validated data containing user information.

        Returns:
            User: The newly created user instance.

        TODO:
            Implement email verification to be sent to the user.
        """

        email = validated_data['email']
        username = validated_data['username']
        password = validated_data['password']
        firstname = validated_data['first_name']
        lastname = validated_data['last_name']
        name = firstname or lastname or username

        # validate required fields
        try:
            validate_required_fields(email, username, firstname, lastname, password)
        except ValueError as e:
            raise serializers.ValidationError({'error': str(e)})

        # validate password complexity
        try:
            validate_password_complexity(password, username, email, firstname, lastname)
        except ValueError as e:
            raise serializers.ValidationError({'error': str(e)})

        # validate username
        try:
            validate_username(username)
        except ValueError as e:
            raise serializers.ValidationError({'error': str(e)})

        # TODO: send email verification to user

        # Extract password from validated data
        # validated_data.pop("password", None)

        print(validated_data)

        user = get_user_model().objects.create_user(**validated_data)

        return user

    def update(self, instance, validated_data):
        """
        Update an existing user instance.

        Args:
            instance (User): The existing user instance to be updated.
            validated_data (dict): Validated data containing updated user information.

        Returns:
            User: The updated user instance.

        """

        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def validate(self, data):
        """
        Validate incoming user data.

        Args:
            data (dict): User data to be validated.

        Raises:
            serializers.ValidationError: If the email or username already exists.

        Returns:
            dict: The validated user data.
        """

        email = data.get('email')
        username = data.get('username')
        if email and get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists')

        if username and get_user_model().objects.filter(username=username).exists():
            raise serializers.ValidationError('Username already exists')
        return data


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for the user registration_authentication token.

    This serializer handles the serialization and deserialization of user registration_authentication tokens.
    It includes custom methods for validating and authenticating user tokens.

    Attributes:
        email (str): The email address of the user.
        password (str): The user's password.

    Methods:
        validate(email or username, password):
            Validate the user's email and password, returning an registration_authentication token if successful.

    Example:
        serializer = AuthTokenSerializer(data=request_data)
        if serializer.is_valid():
            token = serializer.validate()
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='registration_authentication')

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for the user password change.

    This serializer handles the serialization and deserialization of user password change requests.
    It includes custom methods for validating and changing user passwords.

    Attributes:
        old_password (str): The user's current password.
        new_password (str): The user's new password.

    Methods:
        validate(old_password, new_password):
            Validate the user's old and new passwords, returning the new password if successful.

    Example:
        serializer = ChangePasswordSerializer(data=request_data)
        if serializer.is_valid():
            new_password = serializer.validate()
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True, min_length=6)

    def validate(self, attrs, common_passwords=None):
        """
        Validate the user's old and new passwords.
         -  old_password: The user's current password.
         -  new_password: The user's new password.
         -  confirm_password: The user's new password confirmation.

        Returns:
            str: The new password if successful.
        """

        ERROR_MESSAGES = {
            'password_mismatch': _('New password and confirm password do not match'),
            'same_password': _('New password cannot be the same as old password'),
            'no_number': _('Password must contain at least one number'),
            'no_special': _('Password must contain at least one special character'),
            'no_username': _('Password must not contain the username'),
            'no_email': _('Password must not contain the email'),
            'no_firstname': _('Password must not contain the first name'),
            'no_lastname': _('Password must not contain the last name'),
            'no_firstname_lastname': _('Password must not contain the first name and last name'),
            'common_password': _('Password must not be a common password'),
            'no_uppercase': _('Password must contain at least one uppercase letter')
        }

        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError(ERROR_MESSAGES['password_mismatch'], code='password_mismatch')

        if old_password == new_password:
            raise serializers.ValidationError(ERROR_MESSAGES['same_password'], code='password_mismatch')
        try:
            password_validation.validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError(str(e), code='password_mismatch')

        user = self.context['request'].user
        if user.username in new_password:
            raise serializers.ValidationError(ERROR_MESSAGES['no_username'], code='password_mismatch')

        if user.email in new_password:
            raise serializers.ValidationError(ERROR_MESSAGES['no_email'], code='password_mismatch')

        if user.first_name in new_password:
            raise serializers.ValidationError(ERROR_MESSAGES['no_firstname'], code='password_mismatch')

        if user.last_name in new_password:
            raise serializers.ValidationError(ERROR_MESSAGES['no_lastname'], code='password_mismatch')

        if user.first_name + user.last_name in new_password:
            raise serializers.ValidationError(ERROR_MESSAGES['no_firstname_lastname'], code='password_mismatch')

        # password must contain at least one number
        if not any(char.isdigit() for char in new_password):
            raise serializers.ValidationError(ERROR_MESSAGES['no_number'], code='password_mismatch')

        # password must contain at least one special character
        if not any(char in string.punctuation for char in new_password):
            raise serializers.ValidationError(ERROR_MESSAGES['no_special'], code='password_mismatch')

        # password must contain at least one uppercase letter
        if not any(char.isupper() for char in new_password):
            raise serializers.ValidationError(ERROR_MESSAGES['no_uppercase'], code='password_mismatch')

        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for the user forgot password.

    This serializer handles the serialization and deserialization of user forgot password requests.
    It includes custom methods for validating and changing user passwords.

    Attributes:
        email (str): The user's email address.
        username (str): The user's username.

    Methods:
        validate(email):
            Validate the user's email, returning the user if successful.

    Example:
        serializer = ForgotPasswordSerializer(data=request_data)
        if serializer.is_valid():
            user = serializer.validate()
    """
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for the user reset password.

    This serializer handles the serialization and deserialization of user reset password requests.
    It includes custom methods for validating and changing user passwords.

    Attributes:
        email (str): The user's email address.
        username (str): The user's username.
        new_password (str): The user's new password.
        confirm_password (str): The user's new password confirmation.

    Methods:
        validate(password, confirm_password):
            Validate the user's new password, returning the new password if successful.

    Example:
        serializer = ResetPasswordSerializer(data=request_data)
        if serializer.is_valid():
            new_password = serializer.validate()
    """

    email = serializers.EmailField()
    username = serializers.CharField()
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True, min_length=6)

    def validate(self, attrs):
        """
        Validate the user's new password.

        Args:
            attrs (dict): User data to be validated.


        Returns:
            str: The new password if successful.
        """

        new_password = attrs.get('new_password')

        # Add any additional validation logic here
        # Check if the new password contains at least one number
        if not any(char.isdigit() for char in new_password):
            raise serializers.ValidationError("New password must contain at least one number.")

        # Check if the new password contains at least one special character
        if not any(char in string.punctuation for char in new_password):
            raise serializers.ValidationError("New password must contain at least one special character.")

        # Check if the new password contains at least one uppercase letter
        if not any(char.isupper() for char in new_password):
            raise serializers.ValidationError("New password must contain at least one uppercase letter.")

        # Check if the new password contains at least one lowercase letter
        if not any(char.islower() for char in new_password):
            raise serializers.ValidationError("New password must contain at least one lowercase letter.")

        return attrs


class FacebookLoginSerializer(serializers.Serializer):  # facebook access token
    """
    Serializer for the user Facebook login.
     -  fb_access_token: The user's Facebook access token.

    """
    fb_access_token = serializers.CharField(required=True)


class GoogleLoginSerializer(serializers.Serializer):  # google access token
    """
    Serializer for the user Google login.
     -  google_access_token: The user's Google access token.

    """
    google_access_token = serializers.CharField(required=True)


class LinkedInLoginSerializer(serializers.Serializer):  # linkedin access token
    """
    Serializer for the user LinkedIn login.
     -  linkedin_access_token: The user's LinkedIn access token.

    """
    linkedin_access_token = serializers.CharField(required=True)


class ForgotPasswordConfirmSerializer(serializers.Serializer):
    """
    Serializer for the user forgot password.
     -  email: The user's email address.

    """
    pass


class DeleteAccountSerializer(serializers.Serializer):
    """
    Serializer for the user delete account.
     -  email: The user's email address.

    """
    password = serializers.CharField(required=True)
    confirmation = serializers.CharField(max_length=3, min_length=2, required=True)


class EmptySerializer(serializers.Serializer):
    """
    Serializer for the user empty.
    """
    pass


# noinspection PyAbstractClass
class ActivationSerializer(serializers.Serializer):
    """Serializer for the user activation"""
    pass
