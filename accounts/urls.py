from django.urls import path 

from .views import (RegisterView, VerifyOtpView, LoginApiView, 
SendLoginOtpView, ForgetPasswordView, ResetPasswordView, 
LogoutView, RefreshAccessTokenView, ChangePasswordView, GoogleLoginApiView,
UpdateOrganizationView)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('verify/', VerifyOtpView.as_view()),
    path('login/', LoginApiView.as_view()),
    path('send_login_otp/', SendLoginOtpView.as_view()),
    path('forget/',ForgetPasswordView.as_view()),
    path('reset/', ResetPasswordView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('generate_access_token/', RefreshAccessTokenView.as_view()),
    path('change_password/', ChangePasswordView.as_view()),
    path('google-login/', GoogleLoginApiView.as_view()),
    path('update_organization/', UpdateOrganizationView.as_view(), name="update_organization"),
    
    
]
