import re

from django.utils.text import slugify


def slugify_function(value):  # slug function
    """Slugify function"""
    return slugify(re.sub(r'[^\w\s-]', '', value), allow_unicode=True)
