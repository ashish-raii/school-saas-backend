from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import User
from .models import (Classroom, Student, Employee, Designation, 
Department, Organization, Subject, ClassroomSubject, CourseSubject, Course,Section)
from django.shortcuts import get_object_or_404
from accounts.permissions import IsOrganizationAdmin, IsEmployee

from .serializers import ( 
CreateClassroomSerializer, CreateStudentSerializer,  ClassroomDetailsSerializer, 
EmployeeListSerializer, StudentsListSerializer, TeacherProfileSerializer, StudentProfileSerializer,
ClassroomListSerializer, CreateEmployeeSerializer, AddDesignationSerializer, DesignationSerializer, 
CreateDepartmentSerializer, GetDepartmentSerializer, UpdateDepartmentSerializer,
UpdateStudentDetailsSerializer, UpdateEmployeeDetailSerializer,
OrgAdminProfileSerializer, CreateSubjectSerializer, GetSubjectSerializer,
UpdateSubjectSerializer, AssignSubjectToClassSerializer,
GetClassSubjectSerializer,
GetClassSubjectSerializer, CreateSectionSerializer, GetSectionSerializer, UpdateSectionSerializer)

from helpers.api_helpers import api_response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

#########----Classroom View------#######

@extend_schema(request=CreateClassroomSerializer, tags=["Classroom"]) 
class CreateClassroomView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
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
        classroom = serializer.save()
        
        return Response(
            api_response(
                success=True,
                message="Classroom Created Successfully!"
            )
        )


@extend_schema(responses=ClassroomDetailsSerializer(many=True), tags=["Classroom"]) 
class ClassroomDetailsView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self,request,  class_id):
        
        classroom = get_object_or_404(Classroom,id=class_id)
        
        students = Student.objects.filter(
                classroom=classroom, 
                organization=request.user.organization)
        
        teachers = Employee.objects.filter(
            classroom__id = class_id,
            designation__name="Teacher"
        )
        
        sections = Section.objects.filter(
                classroom=classroom, 
                organization=request.user.organization)
        
        response_data = {
            "classroom": classroom,
            "teachers": teachers,
            "students": students,
            "sections" : sections
        }
        
        serializer = ClassroomDetailsSerializer(response_data)
        
        return Response(serializer.data)

#List Nikalne ke liye
@extend_schema(responses=ClassroomListSerializer(many=True), tags=["Classroom"]) 
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

@extend_schema(request=CreateSectionSerializer(many=True), tags=["Section"]) 
class CreateSectionView(APIView):
    # permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    def post(self, request):
        
        serializer = CreateSectionSerializer(
            data= request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        section = serializer.save()
        
        return Response(
            api_response(
                success=True,
                message=f"Section {section.section_name} Created Successfully!",
                data = serializer.data
            )
        )


@extend_schema(responses=GetSectionSerializer(many=True), tags=["Section"]) 
class GetSectionView(APIView):
    def get(self, request):
        section = Section.objects.filter(
                organization=request.user.organization
        )
        serializer = GetSectionSerializer(
            section,
            many=True
            )
        return Response(
            {
                "message": "Sections fetched successfully.",
                "count": section.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

@extend_schema(responses=UpdateSectionSerializer(many=True), tags=["Section"]) 
class UpdateSectionView(APIView):
    def patch(self, request, section_id):
        section = get_object_or_404(
            Section,
            id=section_id,
            organization=request.user.organization
        )
        serializer = UpdateSectionSerializer(
                instance=section,
                data=request.data,
                context={"request": request},
                partial=True
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,)
        
        
#########----Student View------#######

@extend_schema(request=CreateStudentSerializer, tags=["Student"]) 
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
    
@extend_schema(responses=StudentsListSerializer(many=True), tags=["Student"]) 
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

@extend_schema(responses=UpdateStudentDetailsSerializer(many=True), tags=["Student"]) 
class UpdateStudentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    def patch(self, request, classroom_id, roll_no): 
        
        student = get_object_or_404(
            Student,
            classroom_id=classroom_id,
            roll_no=roll_no,
            organization=request.user.organization
        )
        
        serializer = UpdateStudentDetailsSerializer(
                instance=student,
                data=request.data,
                context={"request": request},
                partial=True
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,)

#########----Employee View------#######

@extend_schema(request=CreateEmployeeSerializer, tags=["Employee"]) 
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

@extend_schema(responses=EmployeeListSerializer(many=True), tags=["Employee"]) 
class EmployeeListView(APIView):
    def get(self, request, organization_id):
        
        designation = request.query_params.get("designation")
        department = request.query_params.get("department")
        
        employees = Employee.objects.filter(
            organization_id = organization_id
            
        )
        if department :
            employees = employees.filter(department=department)
        if designation :
            employees = employees.filter(designation=designation)
        
        serializer = EmployeeListSerializer(
            employees,
            many = True
        )

        return Response(serializer.data)

@extend_schema(responses=UpdateEmployeeDetailSerializer(many=True), tags=["Employee"]) 
class UpdateEmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    def patch(self, request, emp_id):
        
        employee = get_object_or_404(
            Employee,
            emp_id = emp_id,
            organization=request.user.organization
        )
        
        serializer = UpdateEmployeeDetailSerializer(
            instance = employee,
            data = request.data,
            context={"request": request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,)

    
@extend_schema(responses=TeacherProfileSerializer(many=True), tags=["Profile"]) 
class UserProfileView(APIView):
    # permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    def get(self, request, organization_id, user_id):
        
        # role = request.query_params.get("role")
        
        user = get_object_or_404(User, id = user_id, organization_id = organization_id)
        
        role = user.role
        print(
            Employee.objects.filter(user=user).values(
                "id", "user_id", "organization_id"
            )
        )

        print(
            Employee.objects.filter(
                user=user,
                organization_id=organization_id
            ).exists()
        )
    
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
        
        elif role == "ORG_ADMIN":
            org_admin = get_object_or_404(
            User.objects.select_related(
            "organization"
            ),
            id=user_id,
            organization_id=organization_id
            )
            serializer = OrgAdminProfileSerializer(org_admin)
        else:

            return Response(
                {"error": "Invalid role"},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        return Response(serializer.data)
        
@extend_schema(request=AddDesignationSerializer(many=True), tags=["Designation"]) 
class AddDesignationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AddDesignationSerializer(
            data = request.data,
            context={
                "request":request
            }  
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message" : "Designation Added Succesfully!"
            }
        )
        
@extend_schema(responses=DesignationSerializer(many=True), tags=["Designation"]) 
class DesignationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        designation = Designation.objects.filter(
            organization=request.user.organization
        )
        
        serializer = DesignationSerializer(
            designation,
            many= True
        )
        
        return Response({"message": "Designation fetched successfully.",
                "count": designation.count(),
                "data": serializer.data
                },
                status=status.HTTP_200_OK,
                        )

#########----Department View------#######

@extend_schema(request=CreateDepartmentSerializer, tags=["Department"]) 
class CreateDepartmentView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    def post(self, request):
        serializer = CreateDepartmentSerializer(
             data = request.data,
             context = {
                 "request" : request
             }
         )
        serializer.is_valid(raise_exception = True)
        department = serializer.save()
        return Response(
                {
                    "message": f"{department.department_name} Department created successfully"
                },
                status=status.HTTP_201_CREATED
            )

@extend_schema(responses=GetDepartmentSerializer(many=True), tags=["Department"]) 
class GetDepartmentView(APIView):        
        permission_classes = [IsAuthenticated]
        
        def get(self, request):
            department = Department.objects.filter(
                organization=request.user.organization
        )
        
            serializer = GetDepartmentSerializer(
            department,
            many=True
            )
            return Response(
            {
                "message": "Departments fetched successfully.",
                "count": department.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

@extend_schema(responses=GetDepartmentSerializer(many=True), tags=["Department"]) 
class GetDepartmentByIdView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, department_id, *args, **kwargs):
            department = get_object_or_404(
                Department.objects.prefetch_related("employee"),
                id = department_id,
                organization=request.user.organization
        )
            serializer = GetDepartmentSerializer(department)
            print(serializer.data)
            print(department.employee.all())
            return Response(
            {
                "message": "Department fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

@extend_schema(responses=UpdateDepartmentSerializer, tags=["Department"]) 
class UpdateDepartmentByIdView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    def patch(self, request, department_id, *args, **kwargs):
        
        department = get_object_or_404(
            Department,
            id=department_id,
            organization=request.user.organization
        )
        
        serializer = UpdateDepartmentSerializer(
            department,
            data = request.data,
            partial = True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            "message": "Department updated successfully.",
             "data": serializer.data
            },
            status=status.HTTP_200_OK,
                        )

#########----Subject Views------#######

@extend_schema(request=CreateSubjectSerializer, tags=["Subject"])         
class CreateSubjectView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    
    def post(self, request):
        serializer = CreateSubjectSerializer(
             data = request.data,
             context = {
                 "request" : request
             }
         )
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(
                {
                    "message": f"Subject created successfully"
                },
                status=status.HTTP_201_CREATED
            )

@extend_schema(responses=GetSubjectSerializer, tags=["Subject"]) 
class GetSubjectView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    def get(self,request):
        
        subject = Subject.objects.filter(
                organization=request.user.organization
        )
        serializer = GetSubjectSerializer(
            subject,
            many=True
            )
        return Response(
            {
                "message": "Subjects fetched successfully.",
                "count": subject.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

@extend_schema(responses=UpdateSubjectSerializer, tags=["Subject"]) 
class UpdateSubjectView(APIView):
    # permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    
    def patch(self, request, subject_code,  *args, **kwargs):
        subject = get_object_or_404(
            Subject,
            subject_code = subject_code,
            organization=request.user.organization
        )
        
        serializer = UpdateSubjectSerializer(
                subject,
                data = request.data,
                partial = True,
                context={"request": request}
        )
        serializer.is_valid()
        serializer.save()
        return Response({
            "message": "Subject updated successfully.",
             "data": serializer.data
            },
            status=status.HTTP_200_OK,
                        )
        
#########----Course Views------#######


        
@extend_schema(responses=AssignSubjectToClassSerializer, tags=["ClassroomSubject"]) 
class AssignSubjectToClassView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = AssignSubjectToClassSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        classroom = serializer.validated_data["classroom"]
        subjects = Subject.objects.filter(
                id__in=serializer.validated_data["subject_id"]
                )
        
        assignments = []
        
        for subject in subjects:
            assignment, created = ClassroomSubject.objects.get_or_create(
            organization=request.user.organization,
            classroom=classroom,
            subject=subject
            )
            assignments.append(assignment)
        return Response(
            {
                "message": "Subjects assigned successfully.",
                "class": classroom.class_name,
                "subjects": [subject.subject_name for subject in subjects]
            },
            status=status.HTTP_201_CREATED
        )
    
@extend_schema(responses=GetClassSubjectSerializer, tags=["ClassroomSubject"]) 
class GetCourseSubjectView(APIView):
    # permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    def get(self,request, classroom_id):
        
        classroomsubject = ClassroomSubject.objects.filter(
                organization=request.user.organization,
                classroom_id = classroom_id
        )
        serializer = GetClassSubjectSerializer(
            classroomsubject,
            many=True
            )
        return Response(
            {
                "message": "Class Subjects fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
        
# @extend_schema(responses=UpdateClassSubjectSerializer, tags=["Course"]) 
# class UpdateClassSubjectView(APIView):
#     # permission_classes = [IsAuthenticated, IsOrganizationAdmin]
#     def patch(self, request, subject_id, classroom_id):
#         subject = get_object_or_404(
#             ClassroomSubject,
#             subject_id = subject_id,
#             classroom_id = classroom_id,
#             organization=request.user.organization
#         )
        
#         serializer = UpdateClassSubjectSerializer(
#                 subject,
#                 data = request.data,
#                 partial = True,
#                 context={"request": request}
#         )

#         serializer.is_valid(raise_exception = True)
#         serializer.save()
#         return Response({
#             "message": "Classroom Subject updated successfully.",
#              "data": serializer.data
#             },
#             status=status.HTTP_200_OK,
#                         )

# @extend_schema(responses=UpdateClassSubjectSerializer, tags=["Course"])
# class UpdateCourseView(APIView):
#     def patch(self, request, course_id):
#         course = get_object_or_404(
#             Course,
#             id = course_id,
#             organization=request.user.organization
#         )
#         serializer = UpdateCourseSerializer(
#                 course,
#                 data = request.data,
#                 partial = True,
#                 context={"request": request}
#         )
#         serializer.is_valid(raise_exception = True)
#         serializer.save()
        
#         return Response({
#             "message": "Course updated successfully.",
#              "data": serializer.data
#             },
#             status=status.HTTP_200_OK,
#                         )

# @extend_schema(responses=GetCourseSerializer, tags=["Course"])
# class GetCourseView(APIView):
#     def get(self,request):
#         course = Course.objects.filter(
#             organization=request.user.organization
#             # course_id = course_id
#         )
#         serializer = GetCourseSerializer(
#             course,
#             many=True
#             )
#         return Response(
#             {
#                 "message": "Courses fetched successfully.",
#                 "data": serializer.data,
#             },
#             status=status.HTTP_200_OK,
#         )
        
# @extend_schema(request=CreateCourseSerializer, tags=["Course"]) 
# class CreateCourseView(APIView):
    # permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    # def post(self, request):
    #     serializer = CreateCourseSerializer(
    #          data = request.data,
    #          context = {
    #              "request" : request
    #          }
    #      )
    #     serializer.is_valid(raise_exception = True)
    #     course = serializer.save()
    #     return Response(
    #             {
    #                 "message": f"{course.course_name} created successfully"
    #             },
    #             status=status.HTTP_201_CREATED
    #         )