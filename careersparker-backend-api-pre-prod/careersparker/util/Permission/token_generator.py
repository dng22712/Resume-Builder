import random

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TokenGenerator(PasswordResetTokenGenerator):
    """
    This component generates a unique verification token.
    It is used when sending an email to for verification and password reset.
    """

    def _make_hash_value(self, user, timestamp):

        if isinstance(user, str):
            # Handle the case when user is a string (e.g., email)
            username = user
        else:
            # Handle the case when user is an object
            username = user.get('email') if hasattr(user, 'get') else user.username
        # try:
        #     username = user.get('email')
        #
        # except AttributeError:
        #     username = user.username

        # Add special characters to the token
        # special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?/"

        # generate 3 characters random special characters
        # special_characters = ''.join(random.choice("!@#$%^&_") for i in range(3))

        token = str(username) + str(timestamp)
        # # randomize the token
        # token = ''.join(random.sample(token, len(token)))
        # print('token1: ', token)

        return token
