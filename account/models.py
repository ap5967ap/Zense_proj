from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, username, phone, dob,pan,password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            return ValueError("Users must have an username")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username,
                          first_name=first_name, last_name=last_name, dob=dob,phone=phone,pan=pan)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, username, phone,pan,dob, password=None):
        user = self.create_user(email=self.normalize_email(
            email), first_name=first_name, last_name=last_name, username=username, phone=phone, pan=pan,dob=dob,password=password)
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
class Account(AbstractUser):
    '''Custom User Model'''
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email=models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    dob = models.DateField()
    pan = models.CharField(max_length=10)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    objects=MyAccountManager()
    def __str__(self):
        return self.username
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email','phone','dob','pan']

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ('-date_joined',)