from django.db import models
from django.utils import timezone
from academics.models import Employee, Student

class EmployeeFaceProfile(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="faces/")
    embedding = models.JSONField()
    registered_at = models.DateTimeField(auto_now_add=True)
    
class StudentFaceProfile(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="faces/")
    embedding = models.JSONField()
    registered_at = models.DateTimeField(auto_now_add=True)
    