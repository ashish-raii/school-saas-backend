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

class Classroom(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    class_name = models.CharField(max_length=20, null=True, blank=True)

    
class Department(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="department",
        null=True,
        blank=True
    )
    
    department_name = models.CharField(max_length=20,blank=False, null=False)
    
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,null=True,blank=True)
    emp_id = models.CharField(max_length=20, null=True,blank=True)
    department = models.ForeignKey(
        Department,
        on_delete= models.CASCADE,
        null=True,
        blank=True,
        related_name= "employee"
    )
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True,blank=True)
    
    classroom = models.ManyToManyField(
        Classroom,
        blank=True,
        null=True,
        related_name= "employee"
    )
    
class Section(models.Model):
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="sections"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE
    )
    section_name = models.CharField(max_length=20, null=True, blank=True)
    students = models.IntegerField(default=0)
    class_teacher = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )
    
    
class TeacherProfile(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE,null=True,blank=True)
    qualification = models.CharField(max_length=100)
    experience = models.CharField(max_length=50)
    
  
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
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE
    )
    
    roll_no = models.CharField(max_length=20,blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    
    address = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact = models.CharField( blank=True, null=True)
    
    session = models.CharField( blank=True, null=True)
    
    def __str__(self):
        return self.first_name
  

class Subject(models.Model):
    subject_name = models.CharField(max_length=20,blank=False, null=False)
    subject_code = models.CharField(max_length=20,blank=False, null=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True,
    blank=True, related_name="subjects", default= None)
    
class ClassroomSubject(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="organization")
    classroom = models.ForeignKey(Classroom,on_delete=models.CASCADE, related_name="classroom_subjects")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="classroom_subjects")
    teacher = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL, 
        null=True,blank=True,
        limit_choices_to={"designation": "Teacher"},  # Optional
        related_name="classroom_subjects")
    
    #Uniqueness ke liye
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["classroom", "subject"],
                name="unique_classroom_subject"
            )
        ]

class Course(models.Model):
    course_name = models.CharField(max_length=50)
    
    organization = models.ForeignKey(
        Organization,
        on_delete= models.CASCADE
    )

class CourseSubject(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="course_organization")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
