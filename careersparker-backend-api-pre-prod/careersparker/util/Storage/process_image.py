import sys
from io import BytesIO

from PIL import Image
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.response import Response

from careersparker import settings
from user.models import ProfilePicture


# -----------------------------------------------
# Add default profile picture if no image is uploaded
# -----------------------------------------------
def default_profile_picture(user, user_profile, pk):
    """
    Add default image if no image is uploaded
    """
    profile_image_local_path = settings.PROFILE_IMAGE_LOCAL_PATH
    profile_image_default = File(open(profile_image_local_path, 'rb'))
    ProfilePicture.objects.filter(user_profile=pk).update_or_create(
        profile_picture=profile_image_default,
        user=user,
        user_profile=user_profile
    )

    return Response({'message': 'Default Profile image updated successfully'}, status=status.HTTP_200_OK)


# -----------------------------------------------
# Convert png, jpeg, jpg to webp
# -----------------------------------------------
def convert_image_webp(image):
    """
    This function converts an image to a desired format based on its content type.

  Args:
      image: A Django InMemoryUploadedFile object representing the image.

  Returns:
      A converted InMemoryUploadedFile object.
    """
    # Check for supported image types (PNG or JPEG)
    if image.content_type in ('image/png', 'image/jpeg', 'image/jpg'):
        converted_rgb = Image.open(image)
        converted_webp = converted_rgb.convert('RGB')
        output = BytesIO()
        converted_webp.save(output, format='webp', quality=100)
        output.seek(0)
        new_filename = "%s.webp" % (image.name.split('.')[0])
        content_type = "image/webp"
        converted_image = InMemoryUploadedFile(
            output,
            'ImageField',
            new_filename,
            content_type,
            sys.getsizeof(output),
            None
        )
        return converted_image
    else:
        return image


# -----------------------------------------------
# check if image is greater than 1240x1754, if yes reduce image size to 1240x1754 and file size to 200kb
# -----------------------------------------------

def check_image_size(image):
    """
       This function checks if an image is greater than 1240x1754 and reduces the image size to 1240x1754 and file size to 300kb if it's more than 800mb.

       Args:
           image: A Django InMemoryUploadedFile object representing the image.

       Returns:
           A converted InMemoryUploadedFile object.
       """
    # Check if image is greater than 1240x1754
    if image.width > 1240 or image.height > 1754:
        converted_rgb = Image.open(image)
        converted_rgb.thumbnail((1240, 1754))
        output = BytesIO()
        converted_rgb.save(output, format='jpeg', quality=100)
        output.seek(0)
        # Check if file size is greater than 800kb
        if sys.getsizeof(output) > 800 * 1024:
            # Calculate dynamic quality to achieve target size
            target_size = 300 * 1024  # Target file size in bytes (300kb)
            original_size = sys.getsizeof(output)  # Original file size in bytes
            quality = int(100 * (target_size / original_size))
            output = BytesIO()
            converted_rgb.save(output, format='jpeg', quality=quality)
            output.seek(0)
        new_filename = "%s.jpg" % (image.name.split('.')[0])
        content_type = "image/jpeg"
        converted_image = InMemoryUploadedFile(
            output,
            'ImageField',
            new_filename,
            content_type,
            sys.getsizeof(output),
            None
        )
        return converted_image
    else:
        return image
