from autoslug import AutoSlugField
from ckeditor.fields import RichTextField
from django.db import models
from django.conf import settings

from util.Storage.media_storage_path import get_upload_cv_template_path, get_upload_cv_template_list_path
from util.general.general_util import slugify_function


# -------------------------------------------------------------------
# CV Builder Models
# -------------------------------------------------------------------

class CvBuilder(models.Model):
    """Model for the CV Builder"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cv_title = models.CharField(max_length=255, blank=True)
    cv_slug = AutoSlugField(populate_from='cv_title', slugify=slugify_function, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cv_title

    class Meta:
        verbose_name = 'Cv'
        verbose_name_plural = 'Cvs'


# -------------------------------------------------------------------
# CV Template List Models
# -------------------------------------------------------------------
class CvTemplateList(models.Model):
    """Model for the CV Template List"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cv_template_list')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='cv_template_list')
    cv_template_name = models.CharField(max_length=255, blank=True)
    cv_template_slug = AutoSlugField(populate_from='cv_template_name', slugify=slugify_function, unique=True, blank=True)
    cv_template_profession = models.CharField(max_length=255, blank=True)
    cv_template_thumbnail = models.ImageField(upload_to=get_upload_cv_template_list_path, blank=True)
    cv_template_thumbnail_small = models.ImageField(upload_to=get_upload_cv_template_path, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cv_template_name

    class Meta:
        verbose_name = 'Cv Template List'
        verbose_name_plural = 'Cv Template Lists'


# -------------------------------------------------------------------
# CV Template Models
# -------------------------------------------------------------------
class CvTemplate(models.Model):
    """CV Template model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cv_templates')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='cv_templates')
    cv_template_name = models.CharField(max_length=255, blank=True)
    cv_template_profession = models.CharField(max_length=255, blank=True)
    cv_template_thumbnail = models.ImageField(upload_to=get_upload_cv_template_path, blank=True)
    cv_template_thumbnail_small = models.ImageField(upload_to=get_upload_cv_template_path, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


# -------------------------------------------------------------------
# CV Employment History Models
# -------------------------------------------------------------------

class EmploymentHistory(models.Model):  # CV Employment History
    """EmploymentHistory model"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cv_employment_history')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='cv_employment_history')
    job_title = models.CharField(max_length=255, blank=True)
    employer_name = models.CharField(max_length=255, blank=True)
    employer_city = models.CharField(max_length=255, blank=True)
    employer_country = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    currently_working_here = models.BooleanField(default=False)
    job_description = RichTextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.job_title

    class Meta:
        verbose_name = 'EmploymentHistory'
        verbose_name_plural = 'EmploymentHistories'  #


# -------------------------------------------------------------------
# CV Education Models
# -------------------------------------------------------------------

class Education(models.Model):
    """Educations model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='educations')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='educations')
    school_name = models.CharField(max_length=255, blank=True)
    school_city = models.CharField(max_length=255, blank=True)
    school_country = models.CharField(max_length=255, blank=True)
    degree = models.CharField(max_length=255, blank=True, )
    field_of_study = models.CharField(max_length=255, blank=True)
    grade = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    currently_studying_here = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.school_name

    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Educations'


# -------------------------------------------------------------------
# CV Skill Models
# -------------------------------------------------------------------


class Skill(models.Model):
    """Skills model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skills')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=255, blank=True)
    skill_level = models.IntegerField(blank=True, null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.skill_name

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'


# -------------------------------------------------------------------
# strength Models
# -------------------------------------------------------------------

class Strength(models.Model):
    """Strengths model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='strengths')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='strengths')
    strength_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.strength_name

    class Meta:
        verbose_name = 'Strength'
        verbose_name_plural = 'Strengths'


# -------------------------------------------------------------------
# CV Award Models
# -------------------------------------------------------------------


class Award(models.Model):
    """Awards model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='awards')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='awards')
    award_title = models.CharField(max_length=255, blank=True)
    award_description = RichTextField(blank=True)
    issuer = models.CharField(max_length=255, blank=True)
    award_url = models.URLField(blank=True)
    award_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.award_title

    class Meta:
        verbose_name = 'Award'
        verbose_name_plural = 'Awards'


# -------------------------------------------------------------------
# CV Certification Models
# -------------------------------------------------------------------

class Certificate(models.Model):
    """Certifications model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certifications')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='certifications')
    certificate_title = models.CharField(max_length=255, blank=True)
    certificate_description = RichTextField(blank=True)
    certificate_url = models.URLField(blank=True)
    certificate_authority = models.CharField(max_length=255, blank=True)
    certificate_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.certificate_title

    class Meta:
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'


# -------------------------------------------------------------------
# Publication  Models
# -------------------------------------------------------------------

class Publication(models.Model):
    """Publications model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='publications')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='publications')
    publication_title = models.CharField(max_length=255, blank=True)
    publication_description = RichTextField(blank=True)
    publication_author = models.CharField(max_length=255, blank=True)
    publication_url = models.URLField(blank=True)
    publication_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.publication_title

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'


# -------------------------------------------------------------------
# Achievement Models
# -------------------------------------------------------------------

class Achievement(models.Model):
    """Achievements model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='achievements')
    achievement_description = RichTextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'


# -------------------------------------------------------------------
# Hobby Models
# -------------------------------------------------------------------

class Hobby(models.Model):
    """Hobbies model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hobbies')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='hobbies')
    hobby_name = models.CharField(max_length=255, blank=True)
    hobby_icon_value = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hobby_name

    class Meta:
        verbose_name = 'Hobby'
        verbose_name_plural = 'Hobbies'


# -------------------------------------------------------------------
# reference Models
# -------------------------------------------------------------------

class Reference(models.Model):
    """References model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='references')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='references')
    reference_name = models.CharField(max_length=255, blank=True)
    reference_position = models.CharField(max_length=255, blank=True)
    reference_company = models.CharField(max_length=255, blank=True)
    reference_email = models.EmailField(blank=True)
    reference_phone = models.CharField(max_length=255, blank=True)
    reference_relationship = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reference_name

    class Meta:
        verbose_name = 'reference'
        verbose_name_plural = 'References'


# -------------------------------------------------------------------
# internship Models
# -------------------------------------------------------------------

class Internship(models.Model):
    """"internship model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='internships')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='internships')
    internship_name = models.CharField(max_length=255, blank=True)
    internship_company = models.CharField(max_length=255, blank=True)
    internship_city = models.CharField(max_length=255, blank=True)
    internship_country = models.CharField(max_length=255, blank=True)
    internship_start_date = models.DateField(blank=True, null=True)
    internship_end_date = models.DateField(blank=True, null=True)
    internship_description = RichTextField(blank=True)
    currently_interning_here = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.internship_name

    class Meta:
        verbose_name = 'internship'
        verbose_name_plural = 'Internships'


# -------------------------------------------------------------------
# Course Models
# -------------------------------------------------------------------
class Course(models.Model):
    """Course Model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cv_courses')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='cv_courses')
    course_name = models.CharField(max_length=255, blank=True)
    course_description = RichTextField(blank=True)
    institution_name = models.CharField(max_length=255, blank=True)
    institution_city = models.CharField(max_length=255, blank=True)
    institution_country = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    currently_studying = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.course_name

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'


# -------------------------------------------------------------------
# Language Models
# -------------------------------------------------------------------
class Language(models.Model):
    """Languages model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='languages')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='languages')
    language_name = models.CharField(max_length=255, blank=True)
    language_proficiency = models.IntegerField(blank=True, null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.language_name

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'


# -------------------------------------------------------------------
# Volunteer Experience Models
# -------------------------------------------------------------------
class Volunteering(models.Model):
    """Volunteering model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='volunteering')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='volunteering')
    organization_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    currently_volunteering = models.BooleanField(default=False)
    description = RichTextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization_name

    class Meta:
        verbose_name = 'Volunteering'
        verbose_name_plural = 'Volunteering'


# -------------------------------------------------------------------
# Social Media Models
# -------------------------------------------------------------------

class social_media(models.Model):
    """Social Media model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_media')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='social_media')
    social_media_name = models.CharField(max_length=255, blank=True)
    social_media_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.social_media_name

    class Meta:
        verbose_name = 'Social Media'
        verbose_name_plural = 'Social Media'


# -------------------------------------------------------------------
# Custom Section Models
# -------------------------------------------------------------------

class CustomSection(models.Model):
    """Custom Section model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_sections')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='custom_sections')
    custom_section_header_title = models.CharField(max_length=255, blank=True, default='Custom Section')
    title = models.CharField(max_length=255, blank=True)
    description = RichTextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    currently_here = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Custom Section'
        verbose_name_plural = 'Custom Sections'


# -------------------------------------------------------------------
# Graph Model
# -------------------------------------------------------------------
class Graph(models.Model):
    """Graph model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='graphs')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='graphs')
    graph_header_title = models.CharField(max_length=255, blank=True, default='Graph')
    graph_name = models.CharField(max_length=255, blank=True)
    graph_value = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.graph_name

    class Meta:
        verbose_name = 'Graph'
        verbose_name_plural = 'Graphs'


# -------------------------------------------------------------------
# Text Section Model
# -------------------------------------------------------------------

class TextSection(models.Model):
    """Text Section model"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='text_sections')
    cv = models.ForeignKey(CvBuilder, on_delete=models.CASCADE, related_name='text_sections')
    text_section_header_title = models.CharField(max_length=255, blank=True, default='Text Section')
    text_section_description = RichTextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Text Section'
        verbose_name_plural = 'Text Sections'
