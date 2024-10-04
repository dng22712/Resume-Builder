import re

import requests
from rest_framework.exceptions import ValidationError


# Facebook
def get_user_details_from_facebook(access_token):
    """
    Extracts user details from Facebook using the provided access token.

    Args:

        access_token: The Facebook access token.

    Returns:

        A dictionary containing user details (email, username, first_name, last_name).

    Raises:

        ValidationError: If the access token is invalid or user details cannot be extracted.
        requests.exceptions.RequestException: If there's an error making the request to Facebook.
    """

    profile_response = requests.get(
        f'https://graph.facebook.com/v8.0/me?access_token={access_token}&fields=name,email,first_name,last_name'
    )

    profile_response_json = profile_response.json()

    if 'error' in profile_response_json:
        raise ValidationError({'error': 'Invalid token'})

    email = profile_response_json['email']
    username = email.split('@')[0]
    username = re.sub(r'\W+', '', username)  # Remove non-alphanumeric characters
    first_name = profile_response_json['first_name'] or username + '1'
    last_name = profile_response_json['last_name'] or username + '2'
    profile_picture = profile_response_json['picture']['data']['url'] or None

    return {
        'email': email,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'profile_picture': profile_picture
    }


# LinkedIn
def get_user_details_from_linkedin(access_token):
    """
    Extracts user details from LinkedIn using the provided access token.

    Args:

        access_token: The LinkedIn access token.

    Returns:

        A dictionary containing user details (email, username, first_name, last_name).

    Raises:

        ValidationError: If the access token is invalid or user details cannot be extracted.
        requests.exceptions.RequestException: If there's an error making the request to LinkedIn.
    """

    profile_response = requests.get(
        'https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,profilePicture(displayImage~:playableStreams))',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    profile_response.raise_for_status()
    email = profile_response.json()['elements'][0]['handle~']['emailAddress']['emailAddress']
    profile_picture = \
        profile_response.json()['elements'][0]['profilePicture']['displayImage~']['elements'][0]['identifiers'][0][
            'identifier'] or None

    username = email.split('@')[0]
    username = re.sub(r'\W+', '', username)  # Remove non-alphanumeric characters
    first_name = profile_response.json()['elements'][0]['firstName'].get('localized', {}).get('en_US', '') or username
    last_name = profile_response.json()['elements'][0]['lastName'].get('localized', {}).get('en_US', '') or username

    return {
        'email': email,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'profile_picture': profile_picture
    }


# Google
def get_user_details_from_google(access_token):
    """
    Extracts user details from Google using the provided access token.

    Args:

        access_token: The Google access token.

    Returns:

        A dictionary containing user details (email, username, first_name, last_name).

    Raises:

        ValidationError: If the access token is invalid or user details cannot be extracted.
        requests.exceptions.RequestException: If there's an error making the request to Google.
    """

    profile_response = requests.get(f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}')
    if not profile_response.ok:
        raise ValidationError({'error': 'Failed to authenticate with Google'})

    data = profile_response.json()
    email = data.get('email')
    username = email.split('@')[0]
    username = re.sub(r'\W+', '', username)  # Remove non-alphanumeric characters
    first_name = data.get('given_name') or username
    last_name = data.get('family_name') or username
    profile_picture = data.get('picture') or None

    return {
        'email': email,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'profile_picture': profile_picture
    }
