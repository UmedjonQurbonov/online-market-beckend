from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    ROLE_CHOISE = (
        ('seller', 'seller'),
        ('buyer', 'buyer'), 
    )

    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=20,  choices=ROLE_CHOISE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    activation_code = models.CharField(max_length=6, blank=True, null=True)
    code_created_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'          
    REQUIRED_FIELDS = ['username']  

    def set_activation_code(self):
        self.activation_code = str(uuid.uuid4())[:6]
        self.code_created_at = timezone.now()
        self.save()