from rest_framework import serializers
from .models import AttendanceSession, StudentAttendance, TeacherAttendance
from academics.models import Classroom, Subject, Employee, ClassroomSubject, Student
from datetime import date, time

class CreateAttendanceSessionSerializer(serializers.ModelSerializer):
    classroom_subject_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassroomSubject.objects.all(),
        source="classroom_subject"
    )
    
    class Meta:
        model = AttendanceSession
        fields =  [
            "classroom_subject_id",
            "period"
        ]
        
    def validate(self, attrs):
        request = self.context["request"]

        teacher = request.user.employee

        classroom_subject = attrs["classroom_subject"]
            
        if teacher.designation.name.lower() != "teacher":
            raise serializers.ValidationError(
                "Only teachers can create attendance sessions."
            )    

        if classroom_subject.organization != request.user.organization:
            raise serializers.ValidationError(
                {"classroom_subject_id": "Invalid classroom subject."}
            )
            
        if classroom_subject.teacher != teacher:
            raise serializers.ValidationError(
            "You are not assigned to this classroom subject."
            )
        
        if AttendanceSession.objects.filter(
            classroom_subject=classroom_subject,
            period=attrs["period"],
            attendance_date=date.today(),
        ).exists():
            raise serializers.ValidationError(
                "Attendance session already exists."
            )
            
        return attrs
    
    def create(self, validated_data):
        request = self.context["request"]

        validated_data["teacher"] = request.user.employee

        return AttendanceSession.objects.create(**validated_data)
    
    
class StudentsAttendanceSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source="student"
    )
    
    class Meta:
        model = StudentAttendance
        fields = [
            "student_id",
            "status",
        ]
class MarkAttendanceSerializer(serializers.Serializer):
    attendance_session_id = serializers.IntegerField()
    students = StudentsAttendanceSerializer(many=True)
    

class GetStudentListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "roll_no",
        ]