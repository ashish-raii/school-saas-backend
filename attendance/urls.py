from django.urls import path 
from .views import *

urlpatterns = [
path('create_attendance_session/', CreateAttendanceSessionView.as_view()),
path('mark_attendance/', MarkStudentAttendanceView.as_view()),
path("session/<int:attendance_session_id>/students/",
        AttendanceSessionStudentsView.as_view(),
        name="attendance-session-students",
    ),
]