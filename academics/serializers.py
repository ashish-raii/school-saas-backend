from rest_framework import serializers
from accounts.models import User
from .models import User, Classroom, Student, Employee, Designation, Department, Subject, ClassroomSubject
from django.db import transaction


    

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
    classroom_id = serializers.CharField()
    
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
            "department" : instance.department,
            "designation" : str(instance.designation)
        }
    
    
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