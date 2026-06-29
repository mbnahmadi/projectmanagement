from enum import unique
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
#User manager
class UserManager(BaseUserManager):
    '''
    اگه مستقیم از create_user یا createsuperuser استفاده کنیم درین صورت این دستورات اعمال میشه و ربطی به پنل ادمین نداره
    '''
    def create_user(self, email, username, password=None, **extra_fields):
        email = self.normalize_email(email)  #نرمالسازی ینی فرم ایمیل رو داشته باشه
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password) #پسورد رو هش میکنه
        user.save()
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        if password is None:
            raise ValueError(_('Superuser must have a password.'))

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email=email, username=username, password=password, **extra_fields)



class CustomUserModel(AbstractUser):
    email = models.EmailField(unique=True)
    last_activity = models.DateTimeField(null=True, blank=True, db_index=True)


    objects = UserManager()

    USERNAME_FIELD = "username"   

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.email}'