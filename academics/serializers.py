from rest_framework import serializers
from accounts.models import User
from .models import User, Classroom, Student, Employee, Designation, Department
from django.db import transaction
from django.shortcuts import get_object_or_404

    

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

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "User with this email already exists."
            })

        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({
                "phone": "User with this phone already exists."
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
            # classroom=validated_data.get("classroom"),
            # first_name=validated_data.get("first_name"),
            # last_name=validated_data.get("last_name"),
            roll_no=validated_data.get("roll_no"),
            father_name = validated_data.get("father_name"),
            mother_name = validated_data.get("mother_name"),
            address = validated_data.get("address"),
            emergency_contact=validated_data.get("emergency_contact"),
            session = validated_data.get("session")
        )

        return student

#########----Employee Serializers------#######

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
        
        designation, created  = Designation.objects.get_or_create(
            name=validated_data["designation_name"].strip(),
            organization=request.user.organization,
            
            
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

#########----ClassRoom Serializers------#######

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
            section=attrs["section"]
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

class ClassroomListSerializer(serializers.Serializer):
    class_id = serializers.IntegerField(source="id")
    class_name = serializers.CharField()
    section = serializers.CharField()

class ClassroomDetailsSerializer(serializers.Serializer):
    
    classroom = ClassroomListSerializer()
    teachers = EmployeeListSerializer(many=True)
    students = StudentsListSerializer(many=True)
    
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
    
class GetDepartmentSerializer(serializers.Serializer):
        department_name = serializers.CharField()
        id =  serializers.CharField()
        organization = serializers.CharField()

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