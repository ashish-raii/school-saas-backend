from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from accounts.permissions import IsEmployee
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from attendance.models import AttendanceSession, StudentAttendance
from academics.models import Student


from attendance.serializers import (CreateAttendanceSessionSerializer, 
MarkAttendanceSerializer, GetStudentListSerializer)

class CreateAttendanceSessionView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    
    def post(self, request):
        serializer = CreateAttendanceSessionSerializer(
            data=request.data,
            context={"request": request}
        )
        
        serializer.is_valid(raise_exception=True)
        attendance_session = serializer.save()
        serializer = CreateAttendanceSessionSerializer(
            attendance_session
            )
        return Response({
        "message": "Attendance session created successfully.",
        "data": serializer.data
    },
    status=status.HTTP_201_CREATED
)
        
        
class MarkStudentAttendanceView(APIView):
    # permission_classes = [IsAuthenticated, IsEmployee]
    @transaction.atomic
    def post(self, request):
        serializer = MarkAttendanceSerializer(
            data=request.data,
            context={"request": request}
        )
        
        serializer.is_valid(raise_exception=True)

        attendance_session = get_object_or_404(
            AttendanceSession,
            id=serializer.validated_data["attendance_session_id"]
            )
        if attendance_session.teacher != request.user.employee:
            return Response(
            {"message": "You are not allowed to mark attendance."},
            status=status.HTTP_403_FORBIDDEN
            )
            
        students = serializer.validated_data["students"]
        attendance_records = []
        for student_data in students:
            if student_data["student"].classroom != attendance_session.classroom:
                raise ValidationError(
                f"{student_data['student'].user.full_name} does not belong to this classroom."
                )
            attendance, created = StudentAttendance.objects.update_or_create(
                attendance_session=attendance_session,
                student=student_data["student"],
                defaults={
                    "status": student_data["status"]
                }
            )
            attendance_records.append(attendance)
        return Response(
            {
                "message": "Attendance marked successfully."
            },
            status=status.HTTP_200_OK
        )

class AttendanceSessionStudentsView(APIView):
    # permission_classes = [IsAuthenticated, IsEmployee]
    def get(self, request, attendance_session_id):
        attendance_session = get_object_or_404(
            AttendanceSession,
            id=attendance_session_id
        )
        if attendance_session.teacher != request.user.employee:
            return Response(
                {
                    "message": "You are not authorized to access this attendance session."
                },
                status=403
            )
        students = Student.objects.filter(
            classroom=attendance_session.classroom_subject.classroom
        ).select_related("user").order_by("roll_no")
        
        serializer = GetStudentListSerializer(
            students,
            many=True
        )
        return Response(
            {
                "attendance_session_id": attendance_session.id,
                "classroom": attendance_session.classroom_subject.classroom.class_name,
                "subject": attendance_session.classroom_subject.subject.subject_name,
                "subject_code": attendance_session.classroom_subject.subject.subject_code,
                "period": attendance_session.period,
                "students": serializer.data,
            }
        )