from django.db import models
from projectapp.models import ProjectModel
from core.files_path import feedback_file_path, feedback_ISO_file_path
from django.utils.translation import gettext_lazy as _

# Create your models here.

class FeedBackModel(models.Model):
    project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE, related_name="feedbacks", verbose_name=_('project'))
    name = models.CharField(verbose_name=_('Name of the employer'), max_length=255)
    phone_number = models.CharField(verbose_name=_('phone number'), help_text="Employer's mobile phone",  max_length=16)
    through = models.CharField(verbose_name=_('How to declare?'), help_text=_('like whats app, call, SMS or some thing else.'), max_length=255)
    date = models.DateField(verbose_name=_('date'))
    message = models.TextField()
    # attachment = models.FileField(upload_to=feedback_file_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Feed Back'
        verbose_name_plural = 'Feed Backs'

    def __str__(self):
        return f"Feedback for {self.project}"


class FeedBackResponseModel(models.Model):
    feedback = models.OneToOneField(FeedBackModel, on_delete=models.CASCADE, related_name="responses", verbose_name=_('feedback'))
    through = models.CharField(verbose_name=_('How to declare?'), help_text=_('like whats app, call, SMS or some thing else.'), max_length=255)
    date = models.DateField(verbose_name=_('date'))
    message = models.TextField()
    iso_form = models.FileField(upload_to=feedback_ISO_file_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Feed Back Response'
        verbose_name_plural = 'Feed Backs Responses'


    def __str__(self):
        return f"Response to {self.feedback}"



class FeedBackAttachmentModel(models.Model):
    feedback = models.ForeignKey(FeedBackModel, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=feedback_file_path, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name