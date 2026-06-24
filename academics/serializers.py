from rest_framework import serializers
from accounts.models import User
from .models import User, Classroom, Student, Employee, Designation
from django.db import transaction
        

class CreateEmployeeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.IntegerField()
    
    password = serializers.CharField(write_only=True)
    
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    
    department = serializers.CharField()
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
        
        designation = Designation.objects.get(
            name=validated_data["designation_name"]
        )
        
        employee = Employee.objects.create(
            user=user,
            emp_id = "TEMP",
            organization=request.user.organization,
            department=validated_data.get("department"),
            designation = designation
        )
        employee.emp_id = f"EMP{employee.id:04d}"
        employee.save(update_fields=["emp_id"])
        
        return employee

class CreateStudentSerializer(serializers.Serializer):

    email = serializers.EmailField()
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField()
    last_name = serializers.CharField()

    roll_no = serializers.CharField()
    classroom_id = serializers.IntegerField()
    
    father_name = serializers.CharField()
    mother_name = serializers.CharField()
    
    address = serializers.CharField()
    emergency_contact = serializers.CharField()
    
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
            role="STUDENT",
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            organization=request.user.organization
        )

        student = Student.objects.create(
            user=user,
            organization=request.user.organization,
            classroom_id= validated_data["classroom_id"],
            # classroom=validated_data.get("classroom"),
            # first_name=validated_data.get("first_name"),
            # last_name=validated_data.get("last_name"),
            roll_no=validated_data.get("roll_no"),
            father_name = validated_data.get("father_name"),
            mother_name = validated_data.get("mother_name"),
            address = validated_data.get("address"),
            emergency_contact=validated_data.get("phone")
        )

        return student

class CreateClassroomSerializer(serializers.Serializer):
    
    class_name = serializers.CharField()
    section = serializers.CharField()
    # session = serializers.CharField()
    
    def validate(self,attrs):
        request = self.context["request"]

        organization = request.user.organization

        if Classroom.objects.filter(
            organization=organization,
            class_name=attrs["class_name"],
            section=attrs["section"],
            academic_session=attrs["session"]
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
            # academic_session =validated_data["session"],
            section = validated_data["section"]
        )   
        
        return classroom
    

class ClassroomStudentsListSerializer(serializers.Serializer):
    name = serializers.CharField(source="user.first_name")
    class_id = serializers.CharField(source="classroom.id")
    roll_no = serializers.CharField()
    
class ClassroomTeacherListSerializer(serializers.Serializer):
    name = serializers.CharField(source="user.first_name")
    emp_id = serializers.CharField(source="user.emp_id")
    department = serializers.CharField(source= "user.department")
    
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
    

class TeachersListSerializer(serializers.Serializer):

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

class ClassroomListSerializer(serializers.Serializer):
    class_id = serializers.IntegerField(source="id")
    class_name = serializers.CharField()
    section = serializers.CharField()


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
    
