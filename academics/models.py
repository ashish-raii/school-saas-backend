from django.db import models
from accounts.models import Organization, User

class Designation(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,null=True,blank=True)
    emp_id = models.CharField(max_length=20, null=True,blank=True)
    department = models.CharField(null=False, blank=False)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True,blank=True)
    
    classroom = models.ManyToManyField(
        "Classroom",
        blank=True,
        null=True,
        related_name= "employee"
    )
    
    
class TeacherProfile(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE,null=True,blank=True)
    qualification = models.CharField(max_length=100)
    experience = models.CharField(max_length=50)
    
  
class Classroom(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    class_name = models.CharField(max_length=20, null=True, blank=True)
    section = models.CharField(max_length=20, null=True, blank=True)
    # academic_session = models.CharField(max_length=20, null=True, blank=True)
    
    
class Student(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='students'
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        
    )
    roll_no = models.CharField(max_length=20,blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    
    address = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact = models.CharField( blank=True, null=True)
    
    session = models.CharField( blank=True, null=True)
    
    def __str__(self):
        return self.first_name
  

