from django.urls import path, include
from .views import ( CreateClassroomView, 
CreateStudentView, ClassroomStudentsView, ClassroomTeachersView, 
StudentsListView, TeachersListView, UserProfileView, ClassroomListView, CreateEmployeeView)

urlpatterns = [
    path('create_student/', CreateStudentView.as_view()),
    path('create_classroom/', CreateClassroomView.as_view()),
    path('create_employee/', CreateEmployeeView.as_view()),
    
    path('classrooms/<int:class_id>/students/',
    ClassroomStudentsView.as_view()),
    
    path('classrooms/<int:class_id>/teachers/',
         ClassroomTeachersView.as_view()),
    
    path('organization/<int:organization_id>/students/',
         StudentsListView.as_view(),
        name= "organzation_students"
    ),
    
    path('organization/<int:organization_id>/teachers/',
         TeachersListView.as_view(),
        name= "organzation_teachers"
    ),
    
    path('organization/<int:organization_id>/classes/',
         ClassroomListView.as_view(),
        name= "organzation_classes"
    ),
    
    path('organization/<int:organization_id>/users/<int:user_id>/',
         UserProfileView.as_view(),
        name= "user_profile"
    ),
     

]

    