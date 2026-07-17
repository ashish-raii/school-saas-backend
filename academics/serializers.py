from rest_framework import serializers
from accounts.models import User
from .models import (User, Classroom, Student,
Employee, Designation, Department, Subject, Course, ClassroomSubject, Section)
from django.db import transaction
from django.db.models import F



    

#########----Student Serializers------#######
class StudentsListSerializer(serializers.Serializer):
    
    id = serializers.CharField(
        source = "user.id"
    )
    email = serializers.CharField(
        source= "user.email"
    )
    phone = serializers.CharField(
        source = "user.phone"
    )
    first_name = serializers.CharField(
        source= "user.first_name"
    )
    last_name = serializers.CharField(
        source = "user.last_name"
    )
    session = serializers.CharField()
    
    roll_no = serializers.CharField()
    class_name = serializers.CharField(
        source= "classroom.class_name"
    )

class CreateStudentSerializer(serializers.Serializer):

    email = serializers.EmailField()
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField()
    last_name = serializers.CharField()

    roll_no = serializers.CharField()
    classroom_id = serializers.IntegerField()
    section_id = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all())
    
    father_name = serializers.CharField()
    mother_name = serializers.CharField()
    
    address = serializers.CharField()
    emergency_contact = serializers.CharField()
    
    session = serializers.CharField(max_length = 20)
    
    def validate(self, data):
        request = self.context["request"]

        email = data.get("email")
        phone = data.get("phone")
        classroom_id = data.get("classroom_id")
        section_id = data["section_id"]

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "User with this email already exists."
            })

        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({
                "phone": "User with this phone already exists."
            })
            
        if section_id.organization != request.user.organization:
            raise serializers.ValidationError({
                "section": "This section is not in your Organization.."
                })
            
        classroom = Classroom.objects.filter(
            id=classroom_id,
            organization=request.user.organization).first()

        if classroom is None:
            raise serializers.ValidationError({
                "classroom_id": "Invalid classroom."
            })
        
        return data

    @transaction.atomic
    def create(self, validated_data):

        request = self.context["request"]

        user = User.objects.create_user(
            email=validated_data.get("email"),
            phone=validated_data.get("phone"),
            password=validated_data.get("password"),
            role="STUDENT",
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            organization=request.user.organization
        )

        student = Student.objects.create(
            user=user,
            organization=request.user.organization,
            classroom_id= validated_data["classroom_id"],
            section=validated_data["section_id"],
            roll_no=validated_data.get("roll_no"),
            father_name = validated_data.get("father_name"),
            mother_name = validated_data.get("mother_name"),
            address = validated_data.get("address"),
            emergency_contact=validated_data.get("emergency_contact"),
            session = validated_data.get("session")
        )
        Section.objects.filter(
            pk=student.section_id
            ).update(
            students=F("students") + 1
            )

        return student

class UpdateStudentDetailsSerializer(serializers.ModelSerializer):
    email =serializers.EmailField(required=False)
    phone = serializers.RegexField(
    regex=r'^\d{10,15}$',
    required=False,
    error_messages={
        "invalid": "Phone number must contain only digits and less than 15 digits."
    })
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    father_name = serializers.CharField()
    mother_name = serializers.CharField()
    address = serializers.CharField()
    emergency_contact = serializers.RegexField(
    regex=r'^\d{10,15}$',
    required=False,
    error_messages={
        "invalid": "Phone number must contain only digits."
    })
    
    class Meta:
        model = Student
        fields =[
            "email",
            "phone",
            "first_name",
            "last_name",
            "father_name",
            "mother_name",
            "address",
            "emergency_contact",   
        ]
        
    def validate(self, attrs):
        student = self.instance
        user = student.user
        # request = self.context.get("request")
        
        email = attrs.get("email")
        phone = attrs.get("phone")
        
        if not attrs:
            raise serializers.ValidationError(
            {
                "message": "At least one field is required to update."
            }
        )
        
        if email:
            if (
                User.objects
                .exclude(id=user.id)
                .filter(email=email) 
                .exists()
            ):
                raise serializers.ValidationError(
                    "Email already exists."
                )

        if phone:
            if (
                User.objects
                .exclude(id=user.id)
                .filter(phone=phone)
                .exists()
            ):
                raise serializers.ValidationError(
                    "Phone already exists."
                )
        return attrs
    
    def update(self, instance, validated_data):
        
        user = instance.user
        
        user.email = validated_data.get("email", user.email)
        user.phone = validated_data.get("phone", user.phone)
        user.first_name = validated_data.get("first_name", user.first_name)
        user.last_name = validated_data.get("last_name", user.last_name)
        user.save()
        
        instance.mother_name = validated_data.get("mother_name", instance.mother_name)
        instance.father_name = validated_data.get("father_name", instance.father_name)
        instance.address = validated_data.get("address", instance.address)
        instance.emergency_contact = validated_data.get("emergency_contact", instance.emergency_contact)
        instance.save()
        
        return instance
    
    def to_representation(self, instance):
        user = instance.user
        return {
            "message" : "Student Data Updated Successfully!",
            "email" : user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name" : user.last_name,
            "mother_name" : instance.mother_name,
            "father_name" : instance.father_name,
            "address" : instance.address,
            "emergency_contact" : instance.emergency_contact
        }
        
#########----Employee Serializers------#######

class CreateEmployeeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.IntegerField()
    
    password = serializers.CharField(write_only=True)
    
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    
    department_name = serializers.CharField()
    designation_name = serializers.CharField()
    
    def validate(self, data):
        
        email = data.get("email")
        phone = data.get("phone")

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "User with this email already exists."
            })

        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({
                "phone": "User with this phone already exists."
            })

        return data
    
    @transaction.atomic
    def create(self, validated_data):

        request = self.context["request"]

        
        user = User.objects.create_user(
            email=validated_data.get("email"),
            phone=validated_data.get("phone"),
            password=validated_data.get("password"),
            role="EMPLOYEE",
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            organization=request.user.organization
        )
        
        designation, created  = Designation.objects.get_or_create(
            name=validated_data["designation_name"].strip(),
            organization=request.user.organization,
        )
        department, created  = Department.objects.get_or_create(
            department_name=validated_data["department_name"].strip(),
            organization=request.user.organization,
        )
        
        employee = Employee.objects.create(
            user=user,
            emp_id = "TEMP",
            organization=request.user.organization,
            department=department,
            designation = designation
        )
        employee.emp_id = f"EMP{employee.id:04d}"
        employee.save(update_fields=["emp_id"])
        
        return employee

class EmployeeListSerializer(serializers.Serializer):

    id = serializers.CharField(
        source = "user.id"
    )
    first_name = serializers.CharField(
        source = "user.first_name"
    )

    emp_id = serializers.CharField()
    
    phone = serializers.CharField(
        source = "user.phone"
    )
    
    email = serializers.CharField(
        source = "user.email"
    )
    
    designation = serializers.CharField()
    department = serializers.CharField()

class UpdateEmployeeDetailSerializer(serializers.ModelSerializer):
    email =serializers.EmailField(required=False)
    phone = serializers.RegexField(
    regex=r'^\d{10,15}$',
    required=False,
    error_messages={
        "invalid": "Phone number must contain only digits and less than 15 digits."
    }) 
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    designation = serializers.SlugRelatedField(slug_field="name",queryset=Designation.objects.all(),required=False)
    department = serializers.CharField()
    
    class Meta:
        model = Employee
        fields =[
            "email",
            "phone",
            "first_name",
            "last_name",
            "designation",
            "department"   
        ]
        
    def validate(self, attrs):
        employee = self.instance
        user = employee.user
        request = self.context.get("request")
        
        email = attrs.get("email")
        phone = attrs.get("phone")
        department = attrs.get("department")
        
        if department:
            if not Department.objects.filter(
            department_name=department
        ).exists():
                raise serializers.ValidationError({
                "department": "This department does not exist. Please select an existing department."
            })
            
        
        if not attrs:
            raise serializers.ValidationError(
            {
                "message": "At least one field is required to update."
            }
        )
        if email:
            if (
                User.objects
                .exclude(id=user.id)
                .filter(email=email) 
                .exists()
            ):
                raise serializers.ValidationError(
                    "User with this Email already exists."
                )

        if phone:
            if (
                User.objects
                .exclude(id=user.id)
                .filter(phone=phone)
                .exists()
            ):
                raise serializers.ValidationError(
                    "User with this Phone already exists."
                )
        return attrs
    
    def update(self, instance, validated_data):
        user = instance.user
        department_name = validated_data.pop("department",None)
        
        if department_name:
            instance.department = Department.objects.get(
            organization=self.context["request"].user.organization,
            department_name=department_name
            )
        
        user.email = validated_data.get("email", user.email)
        user.phone = validated_data.get("phone", user.phone)
        user.first_name = validated_data.get("first_name", user.first_name)
        user.last_name = validated_data.get("last_name", user.last_name)
        user.save()
        
        instance.designation = validated_data.get("designation", instance.designation)
        instance.department = validated_data.get("department", instance.department)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        user = instance.user
        return {
            "message" : "Employee Data Updated Successfully!",
            "email" : user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name" : user.last_name,
            "department" : instance.department.department_name if instance.department else None,
            "designation" : str(instance.designation)
        }
    
    
#########----ClassRoom Serializers------#######

class CreateClassroomSerializer(serializers.Serializer):
    
    class_name = serializers.CharField()
    
    def validate(self,attrs):
        request = self.context["request"]

        organization = request.user.organization

        if Classroom.objects.filter(
            organization=organization,
            class_name=attrs["class_name"],
            
        ).exists():

            raise serializers.ValidationError({
                "class_name" : "This classroom already exists."
            })

        return attrs
        
     
    def create(self, validated_data):
        
        request = self.context.get("request")
        
        classroom = Classroom.objects.create(
            class_name= validated_data["class_name"],
            organization=request.user.organization,    
        )   
        
        return classroom

class ClassroomListSerializer(serializers.Serializer):
    class_id = serializers.IntegerField(source="id")
    class_name = serializers.CharField()
    
class GetSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"
    
class ClassroomDetailsSerializer(serializers.Serializer):
    
    classroom = ClassroomListSerializer()
    teachers = EmployeeListSerializer(many=True)
    students = StudentsListSerializer(many=True)
    sections = GetSectionSerializer(many=True)
    
class CreateSectionSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField()
    classroom_id = serializers.IntegerField()
    class Meta:
        model = Section
        fields = [
            "section_name",
            "classroom_id"
        ]
        
    def validate(self, attrs):
        request = self.context["request"]
        organization = request.user.organization
        
        if Section.objects.filter(
            organization=organization,
            section_name=attrs["section_name"],
        ).exists():

            raise serializers.ValidationError({
                "section_name" : "This Section already exists."
            })
        class_teacher = attrs.get("class_teacher")
        if class_teacher and Section.objects.filter(
            organization=organization,
            class_teacher=class_teacher,
        ).exists():

            raise serializers.ValidationError({
                "class_teacher" : "This Teacher already exists in a Section."
            }) 

        return attrs

    def create(self, validated_data):
        
        request = self.context.get("request")
        
        section = Section.objects.create(
            section_name= validated_data["section_name"],
            classroom_id = validated_data["classroom_id"],
            class_teacher=validated_data.get("class_teacher"),
            organization=request.user.organization
        )   
        
        return section


class UpdateSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = [
            "class_teacher"
        ]
        
    def validate(self, attrs):
        request = self.context["request"]
        organization = request.user.organization
        if Section.objects.filter(
            organization=organization,
            class_teacher=attrs.get("class_teacher", self.instance.class_teacher)
        ).exists():

            raise serializers.ValidationError({
                "class_teacher" : "This Teacher already exists in a Section."
            }) 
        return attrs
            
    def update(self, instance, validated_data):
            instance.class_teacher = validated_data.get("class_teacher", instance.class_teacher)
            
            instance.save()
            return instance
        
    def to_representation(self, instance):
            return {
            "message" : "Section data  Updated Successfully!",
            "class_teacher" : f"{instance.class_teacher.user.first_name} {instance.class_teacher.user.last_name}"
    }
    

#########----Profile Serializers------#######

class BaseProfileSerializer(serializers.Serializer):
    role = serializers.CharField(source="user.role", read_only=True)

    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    phone = serializers.CharField(source="user.phone")
    email = serializers.CharField(source="user.email")

    org_name = serializers.CharField(source="organization.name")

class TeacherProfileSerializer(BaseProfileSerializer):
    
        emp_id = serializers.CharField()
    
        designation = serializers.CharField()    
        department = serializers.CharField()
        
class StudentProfileSerializer(BaseProfileSerializer):
    
    
    roll_no = serializers.CharField()
    
    classroom = ClassroomListSerializer()
    
    # class_name = serializers.CharField(
    #     source = "classroom.class_name"
    # )
    
    mother_name = serializers.CharField()
    
    father_name = serializers.CharField()
    
    address = serializers.CharField()
    
    emergency_contact = serializers.IntegerField()
    
class OrgAdminProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    first_name = serializers.CharField()
    last_name = serializers.CharField()

    phone = serializers.CharField()
    email = serializers.EmailField()
    org_name = serializers.CharField(source="organization.name", read_only=True)
    
    class Meta:
        model = User
        fields = [
            "role",
            "first_name",
            "last_name",
            "phone",
            "email",
            "org_name",
        ]
        
    
#########----Subject Serializers------#######

class CreateSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "subject_name",
            "subject_code"
        ]
    def validate(self,attrs):
        if Subject.objects.filter(
            organization=self.context["request"].user.organization,
            subject_code = attrs["subject_code"],
        ). exists():
            raise serializers.ValidationError(
                    "Subject Code Already Exists!"
            )
            
        if Subject.objects.filter(
            organization=self.context["request"].user.organization,
            subject_name = attrs["subject_name"],
        ). exists():
            raise serializers.ValidationError(
                    "Subject Name Already Exists!"
            )
        return attrs

    
   
        
    
       
    
   
    
    def create(self, validated_data):
        request = self.context.get("request")
        subject = Subject.objects.create(
            subject_name = validated_data["subject_name"],
            subject_code = validated_data["subject_code"],
            organization=request.user.organization,
        )
        return subject
    
class GetSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"

class UpdateSubjectSerializer(serializers.ModelSerializer):
   class Meta:
        model = Subject
        fields = [
            "subject_name",
            "subject_code"
        ]
        def validate(self,attrs):
            if Subject.objects.filter(
                organization=self.context["request"].user.organization,
                subject_code = attrs["subject_code"],
            ). exists():
                raise serializers.ValidationError(
                        "Subject Code Already Exists!"
                )
            
            if Subject.objects.filter(
                organization=self.context["request"].user.organization,
                subject_name = attrs["subject_name"],
            ). exists():
                raise serializers.ValidationError(
                        "Subject Name Already Exists!"
                )
            return attrs
        
        def update(self, instance, validated_data):
            
            instance.subject_name = validated_data.get("subject_name", instance.subject_name)
            instance.subject_code = validated_data.get("subject_code", instance.subject_code)
            
            instance.save()
            return instance
        
        def to_representation(self, instance):
            user = instance.user
            return {
            "message" : "Subject  Updated Successfully!",
            "subject_code" : instance.subject_code,
            "subject_name": instance.subject_name,
            }




class AssignTeacherToClassroomSerializer(serializers.ModelSerializer):
    pass 

#########----Designation Serializers------#######

class AddDesignationSerializer(serializers.Serializer):
    
    designation = serializers.CharField(max_length= 100)
    
    def validate_designation(self, value ):
        request = self.context["request"]
        
        organization = request.user.organization
        
        value = value.strip()
        
        if Designation.objects.filter(
            organization = organization,
            name__iexact = value
        ).exists():
            raise serializers.ValidationError({
            "designation":"Designation already Exists ! Please Select."
        })
        return value
            
    def create(self, validated_data):
        request = self.context.get("request")
        
        designation = Designation.objects.create(
            organization = request.user.organization,
            name = validated_data["designation"]
        )
        return designation
    
class DesignationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    
#########----Department Serializers------#######

class CreateDepartmentSerializer(serializers.Serializer):
    department_name = serializers.CharField()
    
    def validate_department_name(self, value):
        request = self.context.get("request")
        if not value.isupper():
            raise serializers.ValidationError({
                "error": "Department Name must be Capital!"
            })
        
        if Department.objects.filter(
            organization = request.user.organization,
            department_name = value
        ).exists():
            raise serializers.ValidationError({
            "error":"Department already Exists ! Please Select."
        })
        return value
        
    def create(self, validated_data):
        request = self.context.get("request")
        
        department_name = Department.objects.create(
            organization = request.user.organization,
            department_name  = validated_data["department_name"]
        )
        return department_name
    
class DepartmentEmployeeSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    designation = serializers.CharField()
    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "designation",
        ]
        
class GetDepartmentSerializer(serializers.ModelSerializer):
    employee = DepartmentEmployeeSerializer(many=True, read_only=True)
    
    class Meta:
            model = Department
            fields = [
            "id",
            "department_name",
            "organization",
            "employee",
        ]

class UpdateDepartmentSerializer(serializers.Serializer):
        department_name = serializers.CharField()
        
        def validate_department_name(self, value):
            request = self.context.get("request")
            if not value.isupper():
                raise serializers.ValidationError({
                    "error": "Department Name must be Capital!"
                })
            return value
        
        def update(self, instance, validated_data):
            request = self.context.get("request")
            instance.department_name = validated_data.get(
            "department_name",
            instance.department_name
        )
            instance.save()
            return instance
        
        
#########----ClassSubject Serializers------#######


class AssignSubjectToClassSerializer(serializers.ModelSerializer):
    subject_id = serializers.ListField(
        child=serializers.IntegerField()
    )
    classroom_id = serializers.IntegerField()
    class Meta:
        model = ClassroomSubject
        fields = [
            "subject_id",
            "classroom_id",
        ]
    def validate(self, attrs):
        request = self.context["request"]
        organization = request.user.organization
        
        subjects = Subject.objects.filter(
            id__in=attrs["subject_id"],
            organization=organization
        )
        
        if subjects.count() != len(attrs["subject_id"]):
            raise serializers.ValidationError({
         "subject_id": "One or more subjects are invalid."
       })
            
        try:
            classroom = Classroom.objects.get(
        id=attrs["classroom_id"],
        organization=organization
    )
        except Classroom.DoesNotExist:
            raise serializers.ValidationError({
                "classroom_id": "Invalid classroom."
                })
        print("Classroom ID:", attrs["classroom_id"])
        print("Subject IDs:", attrs["subject_id"])      
        existing_subjects = ClassroomSubject.objects.filter(
            organization=request.user.organization,
            classroom=classroom,
            subject__in = subjects
        )
        if existing_subjects.exists():
            subject_names = ", ".join(
            existing_subjects.values_list("subject__subject_name", flat=True))
            raise serializers.ValidationError({
                "error" : f"{subject_names} is already assigned to this classroom"
            })
            
        attrs["classroom"] = classroom
        attrs["subjects"] = subjects
        return attrs
    
class GetClassSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.subject_name", read_only=True)
    subject_code = serializers.CharField(source="subject.subject_code", read_only=True)
    class Meta:
        model = ClassroomSubject
        fields = [
            "classroom_id",
            "subject_name",
            "subject_code"
        ]
        
# class UpdateClassSubjectSerializer(serializers.Serializer):
    
#     classroom_id = serializers.IntegerField()
#     subject_id = serializers.IntegerField()
    
#     def validate(self, attrs):
        
#         request = self.context["request"]
#         organization = request.user.organization
    
#         classroom_id = attrs.get("classroom_id", self.instance.course_id)
#         subject_id = attrs.get("subject_id", self.instance.subject_id)

#         qs = ClassroomSubject.objects.filter(
#             classroom_id = classroom_id,
#             subject_id = subject_id,
#             organization = organization
#         ).exclude(pk=self.instance.pk)
#         if qs.exists():
#             raise serializers.ValidationError(
#                 "This subject is already assigned to this classroom!"
#             ) 
    
#         return attrs
    
#     def update(self, instance, validated_data):
        
#         instance.classroom_id = validated_data.get("classroom_id", instance.classroom_id)
#         instance.subject_id = validated_data.get("subject_id", instance.subject_id)
        
#         instance.save()
#         return instance
    
#     def to_representation(self, instance):
#         return {
#             "subject_id": instance.subject_id,
#             "classroom_id" : instance.classroom.classroom_name
#         }
        
# class UpdateCourseSerializer(serializers.ModelSerializer):
#     course_name = serializers.CharField()
    
#     class Meta:
#         model = Course
#         fields = [
#             "course_name"
#         ]
        
#     def validate_course_name(self, value):
#         request = self.context.get("request")
#         if Course.objects.filter(
#             organization = request.user.organization,
#             course_name = value
#         ).exists():
#             raise serializers.ValidationError({
#             "error":"Course already Exists !"
#         })
#         return value

#     def update(self, instance, validated_data):
#         instance.course_name = validated_data.get("course_name", instance.course_name)
#         instance.save()
#         return instance
    
# class GetCourseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Course
#         fields = "__all__"
   
# class AssignSubjectToCourseSerializer(serializers.Serializer):
#     course_id = serializers.IntegerField()
#     subject_ids = serializers.ListField(
#         child = serializers.IntegerField(),
#         allow_empty=False
#     )
    
#     def validate(self, attrs):
#         request = self.context["request"]
#         organization = request.user.organization
        
#         try:
#             course = Course.objects.get(
#                 id=attrs["course_id"],
#                 organization=organization
#             )
            
#         except Course.DoesNotExist:
#             raise serializers.ValidationError({
#                 "course_id": "Invalid Course."
#             })
            
        
#         subjects = Subject.objects.filter(
#             id__in=attrs["subject_ids"],
#             organization=organization
#         )
        
#         existing_subjects = CourseSubject.objects.filter(
#             organization=request.user.organization,
#             course=course,
#             subject__in = subjects
#         )
#         if existing_subjects.exists():
#             subject_names = ", ".join(
#             existing_subjects.values_list("subject__subject_name", flat=True))
            
#             raise serializers.ValidationError({
#              "subject_ids": f"These subjects are already assigned to the course: {subject_names}"
#         })

#         attrs["course"] = course
#         attrs["subjects"] = subjects

#         return attrs
         
# class CreateCourseSerializer(serializers.ModelSerializer):
#     course_name = serializers.CharField()
    
#     class Meta:
#         model = Course
#         fields = [
#             "course_name"
#         ]
    
#     def validate_course_name(self, value):
#         request = self.context.get("request")
#         if Course.objects.filter(
#             organization = request.user.organization,
#             course_name = value
#         ).exists():
#             raise serializers.ValidationError({
#             "error":"Course already Exists !"
#         })
#         return value

#     def create(self, validated_data):
#         request = self.context.get("request")
        
#         course_name = Course.objects.create(
#             organization = request.user.organization,
#             course_name  = validated_data["course_name"]
#         )
#         return course_name
      