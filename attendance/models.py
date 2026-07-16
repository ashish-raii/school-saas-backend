from django.db import models
from academics.models import Classroom, Subject, Employee, Student, ClassroomSubject
from django.utils import timezone

class AttendanceSession(models.Model):
    # classroom = models.ForeignKey(
    #     Classroom,
    #     on_delete=models.CASCADE
    #     # blank=True,
    #     # null=True
    # )
    # subject = models.ForeignKey(
    #     Subject,
    #     on_delete=models.CASCADE
    # )
    classroom_subject = models.ForeignKey(
        ClassroomSubject,
        on_delete=models.CASCADE
    )
    
    
    teacher = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="teacher_attendances"
    )
    created_at = models.DateTimeField(
        auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True)
    
    period = models.PositiveSmallIntegerField() # Baad me timetable se connect krunga
    
    attendance_date = models.DateField(auto_now_add=True)
    
    
class StudentAttendance(models.Model):
    attendance_session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="student_attendances"
    )
    
    student = models.ForeignKey(
        Student , 
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    
    status = models.CharField(
        max_length=10,
        choices=[
            ("P", "Present"),
            ("A", "Absent"),
            ("L", "Leave")
        ],
        default="P"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attendance_session", "student"],
                name="unique_student_attendance"
            )
        ]
    
class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE  
    )
    
    date = models.DateField(auto_now_add=True)
    
    status = models.CharField(
        max_length=10,
        choices=[
            ("P", "Present"),
            ("A", "Absent"),
            ("L", "Leave"),
        ]
    )
    
    approval_status = models.CharField(
        max_length=10,
        choices=[
            ("A", "Approved"),
            ("R", "Rejected"),
            ("P", "Pending")
        ],
        default="P"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,)
    updated_at = models.DateTimeField(
        auto_now=True,)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "date"],
                name="unique_teacher_attendance"
            )
        ]
        
        