from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import User
from .models import Classroom, Student, Employee
from django.shortcuts import get_object_or_404

from .serializers import ( 
CreateClassroomSerializer, CreateStudentSerializer, ClassroomStudentsListSerializer, ClassroomTeacherListSerializer, 
TeachersListSerializer, StudentsListSerializer, TeacherProfileSerializer, StudentProfileSerializer,
ClassroomListSerializer, CreateEmployeeSerializer)

from helpers.api_helpers import api_response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema


@extend_schema(request=CreateClassroomSerializer) 
class CreateClassroomView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        
        # class_name = validated_data["class_name"]
        # class_id = validated_data["class_id"]
        
        if not request.user.is_staff:
            return Response(api_response(
                success=False,
                message="Only Admin can create classrooms!"
            ))

        serializer = CreateClassroomSerializer(
            data= request.data,
            context={"request": request}
        )
        
        serializer.is_valid(raise_exception=True)
        # validated_data = serializer._validated_data
        
        classroom = serializer.save()
        
        return Response(
            api_response(
                success=True,
                message="Classroom Created Successfully!"
            )
        )

@extend_schema(request=CreateEmployeeSerializer) 
class CreateEmployeeView(APIView):
    def post (self, request):
        serializer = CreateEmployeeSerializer(
            data = request.data,
            context={
                "request":request
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
                {
                    "message": "Employee created successfull"
                },
                status=status.HTTP_201_CREATED
            )

@extend_schema(request=CreateStudentSerializer) 
class CreateStudentView(APIView):
    def post (self, request):
        serializer = CreateStudentSerializer(
            data = request.data,
            context={
                "request":request
            }
        )

        serializer.is_valid(raise_exception=True)
            # validated_data = serializer.validated_data
            # Identifier = validated_data["identifier"]
        student = serializer.save()
        return Response(
                {
                    "message": "Student created successfull"
                },
                status=status.HTTP_201_CREATED
            )
    
@extend_schema(responses=ClassroomStudentsListSerializer(many=True))  
class ClassroomStudentsView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self,request, class_id):
        
        student = Student.objects.filter(
            classroom_id=class_id
        )
        
        serializer = ClassroomStudentsListSerializer(
            student,
            many=True
        )
        
        return Response(serializer.data)
        
@extend_schema(responses=ClassroomTeacherListSerializer(many=True)) 
class ClassroomTeachersView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self,request,  class_id):
        teacher = Employee.objects.filter(
            classroom__id = class_id
        )
        
        serializer = ClassroomTeacherListSerializer(
            teacher,
            many=True
        )
        
        return Response(serializer.data)

@extend_schema(responses=ClassroomListSerializer(many=True)) 
class ClassroomListView(APIView):
    def get(self, request, organization_id):
        
        classes = Classroom.objects.filter(
            organization_id = organization_id
        )
        
        serializer = ClassroomListSerializer(
            classes,
            many = True
        )
        return Response(serializer.data)

@extend_schema(responses=StudentsListSerializer(many=True)) 
class StudentsListView(APIView):
    def get(self, request,organization_id,  *args, **kwargs ):
        
        # organization_id = kwargs.get("organization_id")
        students = Student.objects.filter(
            organization_id = organization_id
        )
        
        serializer = StudentsListSerializer(
            students,
            many=True
            
        )
        return Response(serializer.data)

@extend_schema(responses=TeachersListSerializer(many=True)) 
class TeachersListView(APIView):
    def get(self, request, organization_id):
        # organization_id = kwargs.get("organization_id")
        
        teachers = Employee.objects.filter(
            organization_id = organization_id,
            designation__name = "TEACHER"
        )
        serializer = TeachersListSerializer(
            teachers,
            many = True
        )

        return Response(serializer.data)
    
@extend_schema(responses=TeacherProfileSerializer(many=True)) 
class UserProfileView(APIView):
    def get(self, request, organization_id, user_id):
        
        # role = request.query_params.get("role")
        
        user = get_object_or_404(User, id = user_id, organization_id = organization_id)
        
        role = user.role
        
        if role == "EMPLOYEE":
            teachers = get_object_or_404(Employee.objects.select_related(
                "user",
                 "organization"
            ),
            user=user,
            organization_id=organization_id
            )
        
            serializer = TeacherProfileSerializer(teachers)
        
    
        elif role == "STUDENT":
            students = get_object_or_404(
            Student.objects.select_related(
            "user",
            "organization",
            "classroom"
            ),
            user=user,
            organization_id=organization_id
            )
            serializer = StudentProfileSerializer(students)
        
        else:

            return Response(
                {"error": "Invalid role"},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        return Response(serializer.data)
        
    
        