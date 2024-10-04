import os


# ---------Profile Picture Storage Path---------
def get_upload_path_profile_picture(instance, filename):
    return 'user-media/user-profile/{0}/{1}{2}'.format(instance.user.username, 'profile-picture/',
                                                       os.path.basename(filename))


# ---------CV Template List Storage Path---------
def get_upload_cv_template_list_path(instance, filename):
    return 'cvr-asset/cv-template-list/{0}/{1}'.format('cv-template/', os.path.basename(filename))


# ---------CV Template Storage Path---------
def get_upload_cv_template_path(instance, filename):
    return 'user-media/user-profile/{0}/{1}'.format('cv-template/', os.path.basename(filename))
