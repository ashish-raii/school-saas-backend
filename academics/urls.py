from django.urls import path, include
from .views import ( CreateClassroomView, 
CreateStudentView,  ClassroomDetailsView, 
StudentsListView, EmployeeListView, UserProfileView, 
ClassroomListView, CreateEmployeeView, AddDesignationView, 
DesignationView, CreateDepartmentView, GetDepartmentView, GetDepartmentByIdView,
UpdateDepartmentByIdView)

urlpatterns = [
    path('create_student/', CreateStudentView.as_view()),
    path('create_classroom/', CreateClassroomView.as_view()),
    path('create_employee/', CreateEmployeeView.as_view()),
    
    
    # path('classrooms/<int:class_id>/class_students/',
    # ClassroomStudentsView.as_view()),
    
    path('classrooms/<int:class_id>/class_detail/',
         ClassroomDetailsView.as_view()),
    
    path('organization/<int:organization_id>/students/',
         StudentsListView.as_view(),
        name= "organzation_students"
    ),
    
    path('organization/<int:organization_id>/employee/',
         EmployeeListView.as_view(),
        name= "organzation_employee"
    ),
    
    path('organization/<int:organization_id>/classes/',
         ClassroomListView.as_view(),
        name= "organzation_classes"
    ),
    
    path('organization/<int:organization_id>/users/<int:user_id>/',
         UserProfileView.as_view(),
        name= "user_profile"
    ),
    
    path(
        "designation/add/",
        AddDesignationView.as_view(),
        name="add-designation"
    ),
    
    path(
        "designations/", DesignationView.as_view(),
        name = "designations"
    ),
    
    
    #---------#----Department APIs---------#
    path('create_department/', CreateDepartmentView.as_view()),
    
    path(
        "departments/",
        GetDepartmentView.as_view(),
        name="get_departments"
    ),
    
    path(
        "departments/<int:department_id>/",
        GetDepartmentByIdView.as_view(),
        name="get_department_by_id"
    ),
    
    path(
        "update_department/<int:department_id>/",
        UpdateDepartmentByIdView.as_view(),
        name="update_department_by_id"
    )
     

]

    