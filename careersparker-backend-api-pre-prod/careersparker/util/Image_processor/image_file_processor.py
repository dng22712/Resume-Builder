import sys
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


# convert png to jpg
def convert_png_to_jpg(image):
    """
    Convert png to jpg
    :param image:
    :return:
    """
    if image.content_type == 'image/png':
        converted_rgb = Image.open(image)
        converted_jpg = converted_rgb.convert('RGB')
        output = BytesIO()
        converted_jpg.save(output, format='png', quality=100)
        output.seek(0)

        converted_image = InMemoryUploadedFile(
            output, 'ImageField', "%s.jepg" % image.name.split('.')[0], 'image/jpeg',
            sys.getsizeof(output), None
        )

        return converted_image
    else:
        return image


# --------------Check Profile Image Size----------------
def process_user_profile_images(image):  # Profile Image
    """
    Process User Profile Images
        - Resize Image
        - Save to Bytes
        - Return Bytes
    """

    # Check if resizing is necessary based on image size
    if image.size > 1000000:  # Resize if image size is greater than 1MB
        quality = 30
    else:
        quality = 80  # Keep higher quality for smaller images

    # Process the image
    with Image.open(image) as image_process:
        output = BytesIO()
        image_process.save(output, format='jpeg', quality=quality)
        output.seek(0)
        reduced_image = InMemoryUploadedFile(
            output,
            'ImageField', "%s.jpg" % image.name.split('.')[0], 'image/jpeg',
            sys.getsizeof(output), None
        )

    return reduced_image
