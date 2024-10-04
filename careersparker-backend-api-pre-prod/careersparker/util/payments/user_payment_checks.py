from functools import wraps

from rest_framework import status
from rest_framework.response import Response
from fixed_payments.models import StripeFixedPayments


# ------------------------------------------------------------------------------
# Cv Builder Payment
# ------------------------------------------------------------------------------

def   can_create_cv(user):
    """
        Check if the user has permission to view the Cv Builder Payment.

        Args:
            user (User): The user object.

        Returns:
            bool: True if the user is a Superuser or Admin, False otherwise.
            :param user:
        """

    if user.cv_create_count > 0 or user.is_free:
        return True

    return False


# ------------------------------------------------------------------------------
# Cv Template Payment
# ------------------------------------------------------------------------------

def can_create_template(user):
    """
    Check if the user has permission to view the Cv Builder Payment.

    """

    if user.cv_template_count > 0 or user.is_free:
        return True
    return False


# ------------------------------------------------------------------------------
# Can Download Word
# ------------------------------------------------------------------------------
def can_download_worddoc(user):
    """
    Check if the user has permission to view the Cv Builder Payment.

    """

    if user.cv_word_download_count > 0:
        return True

    return False


# ------------------------------------------------------------------------------
# Can Download PDF
# ------------------------------------------------------------------------------

def can_download_cv_pdf(user):
    """
    Check if the user has permission to view the Cv Builder Payment.

    Args:
        user (User): The user object.

    Returns:
        bool: True if the user is a Superuser or Admin, False otherwise.
        :param user:
    """

    if user.cv_pdf_download_count > 0:
        return True

    return False


# ------------------------------------------------------------------------------
# Premium Required for fixed payment
# ------------------------------------------------------------------------------


def premium_required(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        if request.user.is_free:
            return Response(
                {'message': 'This is a premium feature.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return view_func(request, *args, **kwargs)

    return _wrapped_view
