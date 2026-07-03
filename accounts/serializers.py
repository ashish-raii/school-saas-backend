from rest_framework import serializers
from django.core.validators import EmailValidator, RegexValidator 
from django.core.exceptions import ValidationError
import re
from django.db.models import Q
from rest_framework import serializers
from .models import User
from academics.models import Student, Organization


class IdentifierSerializer(serializers.Serializer):

    identifier = serializers.CharField()
    def validate_identifier(self, value):

        value = value.strip()

        
        if any(char.isalpha() for char in value):

            try:
                EmailValidator()(value)

            except ValidationError:

                raise serializers.ValidationError(
                    "Enter a valid email address."
                )

            return value

        # Phone Validation
        if not value.isdigit():

            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if len(value) != 10:

            raise serializers.ValidationError(
                "Phone number must be exactly 10 digits."
            )

        return value
    
class PasswordValidationSerializer(serializers.Serializer):
    password = serializers.CharField(required=False)
    def validate_password(self, value):
        value = value.strip()
        
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be 8 characters long!"
            )
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "Password must contain atleast one capital letter [A-Z]! "
            )
        if not re.search(r'[a-z]',value):
            raise serializers.ValidationError(
                "Password must contain atleast one small letter[a-z]!"
            )
        if not re.search(r'[0-9]',value):
            raise serializers.ValidationError(
                "Password must contain atleast one number [0-9]! "
            )
        if not re.search(r'[@$!%*?&]', value):
            raise serializers.ValidationError(
                "Password must contain atleast one special character! "
            )
        return value

class VerifyOtpSerializer(serializers.Serializer):
    
    identifier = serializers.CharField()
    otp = serializers.CharField(required= False, allow_blank=True, allow_null=True)
    
    generate_token = serializers.BooleanField(
    required=False,
    default=False
)
    # purpose = serializers.ChoiceField(
    #     choices = [
    #         "register",
    #         "login",
    #         "forgot_password"
    #     ]
    # )
    def validate_otp(self,value):
        value = value.strip()
        
        if len(value) != 4 :
            raise serializers.ValidationError(
                "OTP must be of 4 digits!"
            )
            
        if not value.isdigit():
            raise serializers.ValidationError(
                "OTP must contain digits only!"
            )
        return value
    
class LoginSerializer(IdentifierSerializer, PasswordValidationSerializer):
    
    identifier = serializers.CharField()
    login_method = serializers.ChoiceField(choices=["otp", "password"],required=False)
    # otp = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    
    def validate(self, data):
        login_method = data.get("login_method")
        password = data.get("password")
        otp = data.get("otp")
        
        login_method = str(data.get("login_method")).strip().lower()
        
        if login_method == "password":
            if not password:
                raise serializers.ValidationError(
                    "Password is Required!"
                )
            if otp:
                raise serializers.ValidationError({
                    "otp":
                    "otp should not be provided for password login."
                })
            
        if login_method == "otp":
            if not otp:
                raise serializers.ValidationError(
                    "OTP is Required!"
                )
            if password:
                raise serializers.ValidationError({
                    "password":
                    "Password should not be provided for OTP login."
                })
        return data
    
class RegisterSerializer(IdentifierSerializer, PasswordValidationSerializer):
    
    org_name = serializers.CharField()
    admin_name = serializers.CharField()
    confirm_password = serializers.CharField()
    
    def validate(self,data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        
        if password != confirm_password:
            raise serializers.ValidationError(
                {
                "confirm_password" : "Password do not match!"
            })
        return data
    
class UserResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "email",
            "phone",
            # "identifier"
            "role"
        ]
        
class ResetPasswordSerializer(PasswordValidationSerializer):
    identifier = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
#     generate_token = serializers.BooleanField(
#     required=False,
#     default=False
# )     

    def validate(self,data):
        data = super().validate(data)
        
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        
        self.validate_password(password)
        
        if password != confirm_password:
            raise serializers.ValidationError(
                {
                "confirm_password" : "Password do not match!"
            })
        return data
    
class LogOutSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    # refresh_token = serializers.CharField()
    
class RefreshAccessTokenSerializer(serializers.Serializer):

    identifier = serializers.CharField()
    refresh_token = serializers.CharField()
    
class ChangePasswordSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()
    
    def validate(self, data):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {
                "confirm_password" : "Password do not match!"
            })
        return data
    
class SendLoginOtpSerializer(IdentifierSerializer):
    identifier = serializers.CharField()
    login_method = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
class ForgetPasswordSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    
class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField()
    
class UpdateOrganizationSerializer(serializers.ModelSerializer):
    org_name = serializers.CharField()
    email = serializers.EmailField(required=False)
    phone = serializers.RegexField(
    regex=r'^\d{10,15}$',
    required=False,
    error_messages={
        "invalid": "Phone number must contain only digits."
    })
    admin_name = serializers.CharField(source="first_name",required=False)

    class Meta:
        model = User
        fields = (
            "email",
            "phone",
            "admin_name",
            "org_name",
        )
    
    def validate(self, attrs):
        user = self.instance
        org_name = attrs.get("org_name")
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

        if org_name:
            if (
                Organization.objects.exclude(id=user.organization.id)
                .filter(name=org_name)
                .exists()):
                
                raise serializers.ValidationError({
                "org_name": "Organization with this name already exists."
            })

        return attrs
    
    def update(self, instance, validated_data):
        
        org_name = validated_data.pop("org_name", None)
        
        email = validated_data.get("email")
        phone = validated_data.get("phone")
        admin_name = validated_data.get("admin_name")
        
        if email:
                instance.email = email
                
        if phone:
                instance.phone = phone
                
            
        instance.first_name = validated_data.get(
                "first_name",
                instance.first_name,
            )

        instance.save()
        
        if org_name is not None:
            instance.organization.name = org_name
            instance.organization.save()
        return instance
    
    def to_representation(self, instance):
        
        return {
            "message" : "Details Updated Successfully !",
            "email": instance.email ,
            "phone":  instance.phone,
            "admin_name": instance.first_name,
            "org_name": instance.organization.name
            
        }
    
    

        
        