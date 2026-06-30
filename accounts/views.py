from django.shortcuts import render
from django.conf import settings
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from helpers.api_helpers import api_response
from helpers.auth_helpers import create_user_account
from .models import Organization
from academics.models import Student
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import random
from django.core.cache import cache
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
# from django.core.validators import EmailValidator, RegexValidator 
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from google.oauth2 import id_token
from google.auth.transport import requests

from .serializers import (LoginSerializer, RegisterSerializer, VerifyOtpSerializer, 
UserResponseSerializer, ResetPasswordSerializer, LogOutSerializer, 
RefreshAccessTokenSerializer, ChangePasswordSerializer, 
SendLoginOtpSerializer, ForgetPasswordSerializer, GoogleLoginSerializer)
from django.contrib.auth import get_user_model
User = get_user_model()

@extend_schema(request=RegisterSerializer)   
class RegisterView(APIView):
    
    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        
        # extracting variables
        validated_data = serializer.validated_data

        identifier = validated_data["identifier"]
        org_name = validated_data["org_name"]
        admin_name = validated_data["admin_name"]
        password = validated_data["password"]

        exists = User.objects.filter(Q(email=identifier)|Q(phone=identifier)).exists()
        
        if exists:
            return Response(
                api_response(
                    success=False,
                    message="User Already Exists! Please Login!"
                )
            )
        
        if Organization.objects.filter(name=org_name).exists():
                return Response(
                    api_response(
                        success=False,
                        message="Organization with same name already Exists!"
        ))
            
        otp = random.randint(1000,9999)
        cache.set(
            f"otp_{identifier}",
            {
                "identifier": identifier,
                "org_name": org_name,
                "admin_name": admin_name,
                "password": password,
                "otp": make_password(str(otp))
            },
            timeout=300
            )

        print("OTP:", otp )
        return Response(
            api_response(
                success=True,
                message="OTP is Sent Successfully!",
                data={
                    f"otp" : otp
                }
            )
        )
        
@extend_schema(request=VerifyOtpSerializer) 
class VerifyOtpView(APIView):       #OTP Verify karwane ke liye 
    def post(self, request):
        
        serializer = VerifyOtpSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        identifier = validated_data["identifier"]
        otp = validated_data["otp"]
        generate_token = validated_data.get("generate_token", False)
        
        otp_data = cache.get(f"otp_{identifier}")
        
        
        
        if not otp_data:
                return Response(
                api_response(
                    success=False,
                    message="OTP Expired or Invalid!"
                )
                )
            
        stored_otp = otp_data.get("otp")
        if not stored_otp:
            return Response(
                api_response(
                    success=False,
                    message="OTP is Expired!"
                )
            ) 
        
        if not check_password(str(otp), stored_otp):
            return Response(
                api_response(
                    success=False,
                    message="Invalid OTP"
                )
            )
            
        cache.set(
            f"verified_{identifier}",
            {
                "verified": True
            },
            timeout=300
        )
        
        user = None
        if otp_data.get("org_name"): 
        
            registration_data = cache.get(f"otp_{identifier}")
            organization = Organization.objects.create(
                name=registration_data["org_name"]
                )
            user = create_user_account(
                identifier=identifier,
                password=registration_data["password"],
                role="ORG_ADMIN",
                organization=organization,
                first_name=registration_data["admin_name"]
            )
        else:
            user = User.objects.filter(
                Q(email=identifier) | Q(phone=identifier)
            ).first()
            
        cache.delete(f"otp_{identifier}")
        
            
        if generate_token:
                # user = User.objects.filter(Q(email=identifier) | Q(phone=identifier)).first()
                if not user:
                        return Response(
                            api_response(
                                success=False,
                                message="No User Found!"
                            )
                        )
        
                user_data = UserResponseSerializer(user).data
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                cache.delete(f"verified_{identifier}")

                user_data["organization"] = {
                        "id": user.organization.id,
                        "name": user.organization.name,
                    }
                user_data["access_token"] = str(access)
                
                response =  Response(
                        api_response(
                            success=True,
                            message=f"Welcome  {user.first_name}",
                            data={
                                "user_data": user_data
                            }   
                        )
                    )
                
                response.set_cookie(
                        "refresh_token",
                        str(refresh),
                        httponly=True,
                        secure=False,
                        samesite="Lax"
                    )
                
                return response
            
        return Response(
            api_response(
                success=True,
                message="OTP Verified Successfully!"
            )
        )
        
@extend_schema(request=SendLoginOtpSerializer) 
class SendLoginOtpView(APIView):        #Login Using OTP 
    def post(self, request):
        serializer = SendLoginOtpSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        identifier = validated_data["identifier"]
        login_method = validated_data.get("login_method")
        
            
        exists = User.objects.filter(Q(email=identifier)|Q(phone = identifier)).first()
        
        if exists:
            if login_method == "otp":
                login_otp = random.randint(1000, 9999)
        
                cache.set(
                    f"otp_{identifier}",
                    {
                        "identifier": identifier,
                        "org_name": None,
                        "admin_name": None,
                        "password": None,
                        "otp": make_password(str(login_otp))
                    },
                    timeout=300
                    )
                print(login_otp)
                
            elif login_method == "password":
                return Response(api_response(
                    success=True,
                    message="please login with your password!"
                ))
                
            response_data = {}
            if settings.DEBUG:
                response_data["otp"] = login_otp  
                
            return Response(
                api_response(
                   success=True,
                   message="OTP sent Successfully!",
                   data= response_data
                )
            )
                
                
         
        # 
                 
        return Response(
            api_response(
                success=False,
                message="User not Found!"
               )
        )
        
@extend_schema(request=LoginSerializer)        
class LoginApiView(APIView):        # Login Karwane ke liye 
    def post(self, request):
        
        serializer = LoginSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        identifier = validated_data["identifier"]
        # otp = validated_data.get("otp")                   #.get isliye lagayenge kyuki field optional hai
        login_method = validated_data["login_method"] 
        password = validated_data.get("password") #.get isliye lagayenge kyuki field optional hai
        
        user = User.objects.filter(Q(email = identifier)| Q(phone=identifier)).first()
        if not user:
            return Response(
                api_response(
                    success=False,
                    message="No User Found!"
                )
            )
        
        if login_method == "password":
            
            if not check_password(str(password), user.password):
                return Response(
                    api_response(
                        success=False,
                        message="Password is Wrong!"
                    )
                )
                
        elif login_method == "otp":
            
            verified_data = cache.get(f"verified_{identifier}")
            
            if not verified_data or not verified_data.get("verified"):
                # print("CACHE:", cache.get(f"verified_{identifier}"))
                # print("KEY:", f"verified_{identifier}")
                
                return Response(
                    api_response(
                        success=False,
                        message="OTP verification required!"
                    )
                )
                
            cache.delete(f"verified_{identifier}")
            
        
        # cache.delete(f"login_otp_{identifier}")
        user_data = UserResponseSerializer(user).data
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        
        user_data["organization"] = {
                        "id": user.organization.id,
                        "name": user.organization.name,
                    }
        user_data["access_token"] = str(access)
        
        response = Response(
                api_response(
                    success=True,
                    message=f"You are loggedIn Successfully {user.first_name}",
                    data={
                        "user_data" : user_data,
                        # "access" : str(refresh.access_token),
                        # "refresh" : str(refresh)
                    }
                )
            )
        response.set_cookie(
            key="refresh_token",
            value=access,
            httponly=True,
            secure=False,      #True ho jayega jab production me jayega tab
            samesite="Lax",
            max_age=60*60
        )
        
        return response

@extend_schema(request=GoogleLoginSerializer)    
class GoogleLoginApiView(APIView):
    def post(self, request):
        
        serializer = GoogleLoginSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        token = serializer.validated_data["token"]
        try:
            id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        except ValueError:
            return Response(
            api_response(
                success=False,
                message="Invalid Google token."
                ),
                status=400
            )
            
        email = id_info["email"]
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                api_response(
                    success=False,
                    message="User not found."
                ),
                status=404
            )

        return Response(
            api_response(
                success=True,
                message="User exists."
            )
        )
        
        # return Response({
        #     "message": "Token Received"
        # })
    
@extend_schema(request=ForgetPasswordSerializer) 
class ForgetPasswordView(APIView):

    def post(self, request):
        serializer = ForgetPasswordSerializer(
            data= request.data
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        identifier =validated_data["identifier"]
        
        exists = User.objects.filter(Q(email=identifier)| Q(phone=identifier)).exists() #checks if the user exists already
        if not exists:
            return Response(
                api_response(
                    success=False,
                    message="User Not Found"
                )
            )
        
        otp = random.randint(1000,9999) #Generates a Random OTP
        
        cache.set(
            f"otp_{identifier}",{
            "otp": make_password(str(otp))
        },
            timeout=300 
        )               #Saving the OTP in the cache with identifier and otp and timeout limit.
        
        print("OTP Saved:", otp)
        
        return Response(
        api_response(
        success=True,
        message="OTP Sent Successfully!",
        data={
                    f"otp" : otp
                }
    )
)
        
@extend_schema(request=ResetPasswordSerializer) 
class ResetPasswordView(APIView):
    def post(self,request):
        serializer = ResetPasswordSerializer(
            data= request.data
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        identifier = validated_data["identifier"]
        generate_token = validated_data.get("generate_token")
        password = validated_data["password"]
        # confirm_passowrd = validated_data["confirm_password"]
        
        
        user = User.objects.filter(Q(email=identifier)|Q(phone=identifier)).first() #access the user if any exist with the same email or phone 
        
        if not user:
            return Response(
                api_response(
                    success=False,
                    message="User not Found!"
                )
            )
        
        verified_data = cache.get(f"verified_{identifier}")
            
        if not verified_data or not verified_data.get("verified"):
                # print("CACHE:", cache.get(f"verified_{identifier}"))
                # print("KEY:", f"verified_{identifier}")
                
            return Response(
                api_response(
                    success=False,
                    message="OTP verification required!"
                )
            )
            
        
            
        if check_password(password , user.password): #compare between new password and current password 
            return Response(
                api_response(
                    success= False,
                    message="New Password cannot be same as last Password. Try a Different Password."
                )
            )    
        
        user.set_password(password) #sets new password as password 
        user.save()
        
        cache.delete(f"verified_{identifier}")  #del the cached data of the current user
        
        
        
        return Response(
            api_response(
                success=True,
                message="Password Reset Successfully!"
            )
        )                
        
@extend_schema(request=LogOutSerializer)    
class LogoutView(APIView):
    def post(self, request):
        serializer = LogOutSerializer(
            data= request.data
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        identifier = validated_data["identifier"]
        refresh_token = request.COOKIES.get("refresh_token") #Collecting refresh token from the user 
        
        try:
            token = RefreshToken(refresh_token)  #creates a refresh token object using the refresh_token collected by the user above.
            token.blacklist() #blacklist the refresh_token
            
            return Response(
                api_response(
                    success=True,
                    message="Logged Out Successfully!"
                )
            )
        except Exception:
            return Response(
                api_response(
                    success=False,
                    message="Invalid Token"
                )
            )
        
@extend_schema(request=RefreshAccessTokenSerializer)  
class RefreshAccessTokenView(APIView):
    def post(self, request):
        serializer = RefreshAccessTokenSerializer(
            data = request.data
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data 
        
        refresh_token = validated_data['refresh_token'] #Collect refresh token from the user.
        
        # if not refresh_token: 
        #     return Response(
        #         api_response(
        #             success=False,
        #             message="Refresh Token is Required!"
        #         )
        #     )
        try:
            token = RefreshToken(refresh_token) #creates a refresh token object using the token collected by the user.
            return Response(
                api_response(
                    success=True,
                    message="Access Token Generated Successfully!",
                    data={
                        "access" : str(token.access_token) #generates access token by using refresh token.
                    }
                )
            )
        except TokenError:
            return Response(
                api_response( 
                    success=True,
                    message="Token is Blacklisted Already !"
                )        
                )
        
@extend_schema(request=ChangePasswordSerializer)  
class ChangePasswordView(APIView):
    def post (self, request):
        serializer = ChangePasswordSerializer(
            data = request.data
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data 
        
        identifier = validated_data["identifier"]
        current_password = validated_data["current_password"].strip()
        new_password = validated_data["new_password"]
        confirm_password = validated_data["confirm_password"]
        
        print(current_password)
        
        
        
        user = User.objects.filter(Q(email=identifier)| Q(phone= identifier)).first()
        
        if not user:
                return Response(
            api_response(
                success=False,
                message="User not found!"
            )
        )
            
        if not check_password( current_password, user.password):
                return Response(
                    api_response(
                        success= False,
                        message="Password is Wrong!"
                    )
                )
        user.set_password(new_password)
        user.save()
        return Response(
            api_response(
                success=True,
                message="Password Changed Successfully!"
            )
        )
        
       
       
        
