from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.core.files import File
from careersparker import settings
from user import models
from user.models import User
from util.general.send_email import send_user_activation_email


# ----------------- Create User Profile -----------------

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print("sINGAL")
        profile_image_local_path = settings.PROFILE_IMAGE_LOCAL_PATH
        print(profile_image_local_path)
        models.Profile.objects.create(user=instance, id=instance.id)
        profile_image = File(open(profile_image_local_path, 'rb'))  # open the file in read mode
        models.ProfilePicture.objects.create(user_profile_id=instance.id, user_id=instance.id,
                                             profile_picture=profile_image)

        # call send_activation_email function
        send_user_activation_email(instance, user=instance)


# ----------------- User Login Signal -----------------
@receiver(user_logged_in)
def user_login(request, user, **kwargs):
    """

    """

    print("User Not Activated")

    # TODO - Implement user login signal
    # if not created:
    #     instance.save()
    #     # call send_activation_email function
    #     send_activation_email(instance, user=instance)
