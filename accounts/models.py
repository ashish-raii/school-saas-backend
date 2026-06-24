from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractUser



class UserManager(BaseUserManager):
    def create_user(self,email, phone, password=None, **extra_fields):
        if not email and not phone:
            raise ValueError("Either Phone or Email is Required!")
        if email:
            email = self.normalize_email(email)
        else: 
            email = None
        if phone == "":
            phone = None
            
        user = self.model(
            email=email,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email=None, phone=None, password=None, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(
            email=email,
            phone=phone,
            # password=password,
            **extra_fields
        )
        
        

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    

    
class User(AbstractUser):
    
    username = None
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    
    Role_Choices = (
        ('SUPER_ADMIN' , 'super admin'),
        ('ORG_ADMIN', 'org admin'),
        ("TEACHER", 'teacher'),
        ('STUDENT', 'student'),
    )
    
    role = models.CharField(
        max_length=20,
        choices=Role_Choices
    )
    
    email = models.EmailField(
        max_length=50,
        null=True,
        unique=True,
        blank=True
        ) 
    
    phone = models.CharField(
    
        max_length = 15,
        null = True,
        unique = True,
        blank=True
    )
    
    first_name = models.CharField(
    max_length=100,
    null=True,
    blank=True
)
    last_name = models.CharField(
    max_length=100,
    null=True,
    blank=True
)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']
    
    objects = UserManager()
    

    
    
    