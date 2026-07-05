from django.urls import path, include
from .views import ( CreateClassroomView, 
CreateStudentView,  ClassroomDetailsView, 
StudentsListView, EmployeeListView, UserProfileView, 
ClassroomListView, CreateEmployeeView, AddDesignationView, 
DesignationView, CreateDepartmentView, GetDepartmentView, GetDepartmentByIdView,
UpdateDepartmentByIdView, UpdateStudentDetailView, UpdateEmployeeDetailView, CreateSubjectView, 
GetSubjectView, UpdateSubjectView,AssignSubjectToClassroomView, GetClassroomSubjectView,
UpdateClassroomSubjectView)

urlpatterns = [
    path('create_student/', CreateStudentView.as_view()),
    path(
        "update_student/<int:classroom_id>/<int:roll_no>",
        UpdateStudentDetailView.as_view(),
        name="update_student_by_class&_roll_no"
    ),
    
    
    path('organization/<int:organization_id>/students/',
         StudentsListView.as_view(),
        name= "organzation_students"
    ),
    

    path('create_classroom/', CreateClassroomView.as_view()),
    path('classrooms/<int:class_id>/class_detail/',
         ClassroomDetailsView.as_view()),
    
    

    path('create_employee/', CreateEmployeeView.as_view()),    
    path('organization/<int:organization_id>/employee/',
         EmployeeListView.as_view(),
        name= "organzation_employee"
    ),
    
    path(
        "update_employee/<str:emp_id>/",
        UpdateEmployeeDetailView.as_view(),
        name="update_employee_by_emp_id"
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
    
    
    #---------#----Department URLs---------#
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
    ),
    
    #---------#----Subject URLs---------#
    
    path('create_subject/', CreateSubjectView.as_view()),
    
    path(
        "subjects/",
        GetSubjectView.as_view(),
        name="get_subjects"
    ),
    
    path(
        "update_subject/<str:subject_code>/",
        UpdateSubjectView.as_view(),
        name="update_subject"
    ),
    
    path(
        "assign_subject/",
        AssignSubjectToClassroomView.as_view(),
        name="assign_subject"
    ),
    
    
    
    path(
        "classroom_subject/<str:classroom_id>/",
        GetClassroomSubjectView.as_view(),
        name="get_classroomsubject"
    ),
    
    path(
        "update_classroomsubject/<int:classroom_id>/<int:subject_id>/",
        UpdateClassroomSubjectView.as_view(),
        name="update_classroomsubject"
    ),
]

    