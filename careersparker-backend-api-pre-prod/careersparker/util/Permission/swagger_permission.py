from rest_framework import permissions

from user.models import User


class SwaggerPermission(permissions.BasePermission):  # swagger user_permission
    """
    Custom permission class for controlling access to Swagger documentation.

    Only Superusers and Admins are allowed to view the Swagger documentation.

    Methods:
        has_permission(self, user): Check if the user has permission to view the Swagger documentation.

    """

    @staticmethod
    def has_swagger_permission(user):
        """
        Check if the user has permission to view the Swagger documentation.

        Args:
            user (User): The user object.

        Returns:
            bool: True if the user is a Superuser or Admin, False otherwise.
        """
        # print('self: ', self)
        # print('user: ', user)
        # get user_role from user
        user_role = user.role
        # print('user_role: ', user_role)

        # Allow only Superuser and Admin to view swagger
        if user_role == User.RoleType.ROLE_ADMIN or user.is_superuser:
            return True

        else:
            return False
