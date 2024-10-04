from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin, Group, Permission
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from careersparker import settings
from util.Storage.media_storage_path import get_upload_path_profile_picture
from util.user.user_validator import validate_username, validate_password_complexity, validate_required_fields


class UserManager(BaseUserManager):
    """
    Custom user model manager where

    - email and username is the unique identifiers for registration_authentication
    - email and username should be required and lowercase
    - username should not contain special characters
    - username should not contain dots, "/" or spaces
    - password should be required
    - password should be at least 6 characters
    - password should contain at least one uppercase letter
    - password should contain at least one lowercase letter
    - password should contain at least one number
    - password should contain at least one special character
    - password should not contain username
    - password should not contain email
    - password should not contain first name and last name

    """

    def create_user(
            self,
            email,
            username,
            first_name,
            last_name,
            password=None,
            role='User',
            is_verified=False,
            is_active=False,
            **extra_fields
    ):
        """Create, save and return a new user"""

        # Create and save a♦ User with the given email OR username and password.

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_verified=is_verified,
            is_active=is_active,
            **extra_fields
        )

        # set password
        user.set_password(password)

        # save user
        user.save(using=self._db)

        return user

    # ------------------------------------------------------------------------------
    # Create and save a SuperUser with the given email OR username and password.
    # ------------------------------------------------------------------------------

    def create_superuser(self, email, username, first_name, last_name, password):
        """
        Create and save a SuperUser with the given email OR username and password.

        """

        # validate required fields
        validate_required_fields(email, username, first_name, last_name, password)

        # validate password complexity
        validate_password_complexity(password, username, email, first_name, last_name)

        # validate username
        validate_username(username)

        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role='Admin',
            is_verified=True,
            is_active=True,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.is_active = True
        user.save(using=self._db)  # save user
        refresh = RefreshToken.for_user(user)  # generate refresh token
        return user, refresh


# ------------------------------------------------------------------------------
# User Model
# ------------------------------------------------------------------------------

class User(AbstractUser, PermissionsMixin):
    """
    Represents a user in the system, managing registration_authentication, authorization, and basic profile information.

    Inherits from `AbstractBaseUser` to provide custom user model functionality and `PermissionsMixin`
    to enable Django's built-in permission framework for authorization.
    """

    class RoleType(models.TextChoices):
        """
        Defines the available role types for users, each with a descriptive label.
        """

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    last_password_attempt = models.DateTimeField(null=True, blank=True)
    temporary_password_created_at = models.DateTimeField(null=True, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    cv_create_count = models.IntegerField(default=0)
    cv_template_count = models.IntegerField(default=0)
    cv_pdf_download_count = models.IntegerField(default=0)
    cv_word_download_count = models.IntegerField(default=0)
    total_number_of_purchase = models.IntegerField(blank=True, default=0)
    subscription_status = models.BooleanField(default=False)
    role = models.CharField(max_length=255, choices=RoleType.choices, default='User')
    subscription_type = models.CharField(max_length=255, blank=True, default='free')
    is_free = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, )
    updated_at = models.DateTimeField(auto_now=True, )

    objects = UserManager()  # Custom user manager

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    # Custom related names to resolve clashes
    groups = models.ManyToManyField(Group, related_name='user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='user_permissions')

    def __str__(self):  #
        return self.email

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    # is_free to True
    def set_user_is_free_to_true(self):
        self.is_free = True
        self.save()

    # set is_free to False
    def set_user_is_free_to_false(self):
        self.is_free = False
        self.save()

    # deduct cv create count
    def deduct_cv_create_count(self):
        self.cv_create_count -= 1

        self.save()

    # deduct cv template count
    def deduct_cv_template_count(self):
        self.cv_template_count -= 1
        self.save()

    # deduct pdf download count
    def deduct_pdf_download_count(self):
        self.cv_pdf_download_count -= 1
        self.save()

    # deduct word download count
    def deduct_word_download_count(self):
        self.cv_word_download_count -= 1
        self.save()


# ------------------------------------------------------------------------------
# User Profile Model
# ------------------------------------------------------------------------------
class Profile(models.Model):
    """
    Represents a user profile in the system, managing user profile information
    """

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    title_before = models.CharField(max_length=255, blank=True)
    title_after = models.CharField(max_length=255, blank=True)
    about = RichTextField(blank=True)
    phone_number = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=255, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)
    website = models.URLField(max_length=255, blank=True)
    linkedin = models.URLField(max_length=255, blank=True)


# ------------------------------------------------------------------------------
# User Profile Picture Model
# ------------------------------------------------------------------------------
class ProfilePicture(models.Model):
    """Database model for profile picture image"""

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_images')
    user_profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='profile_images')
    profile_picture = models.ImageField(upload_to=get_upload_path_profile_picture, default='default.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'User Profile Picture'
        verbose_name_plural = 'User Profile Picture'


# ------------------------------------------------------------------------------
# User Account
# ------------------------------------------------------------------------------

class Account(models.Model):
    """
    Represents a user account in the system, managing user account information
    """

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_account')
    account_type = models.CharField(max_length=255, blank=True)
    account_start_date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'User Account'
        verbose_name_plural = 'User Account'
