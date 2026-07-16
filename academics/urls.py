from django.urls import path, include
from .views import ( CreateClassroomView, 
CreateStudentView,  ClassroomDetailsView, 
StudentsListView, EmployeeListView, UserProfileView, 
ClassroomListView, CreateEmployeeView, AddDesignationView, 
DesignationView, CreateDepartmentView, GetDepartmentView, GetDepartmentByIdView,
UpdateDepartmentByIdView, UpdateStudentDetailView, UpdateEmployeeDetailView, CreateSubjectView, 
GetSubjectView, UpdateSubjectView, CreateCourseView, AssignSubjectToCourseView, GetCourseSubjectView,
UpdateCourseSubjectView, UpdateCourseView, GetCourseView)

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
    
    
    #---------#----Course URLs---------#
    path('create_course/', CreateCourseView.as_view()),
    
    path(
        "update_course/<int:course_id>/",
        UpdateCourseView.as_view(),
        name="update_course"
    ),
    
    path(
        "assign_subject/",
        AssignSubjectToCourseView.as_view(),
        name="assign_subject"
    ),
    
    path(
        "get_course_subject/<str:course_id>/",
        GetCourseSubjectView.as_view(),
        name="get_coursesubject"
    ),
    
    path(
        "update_course_subject/<int:course_id>/<int:subject_id>/",
        UpdateCourseSubjectView.as_view(),
        name="update_classroomsubject"
    ),
    
    path(
        "get_courses/",
        GetCourseView.as_view(),
        name="get_course"
    ),
    
]

    