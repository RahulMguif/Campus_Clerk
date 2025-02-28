from django.urls import path
from staff_advisor import views

urlpatterns = [
    path('staff_home/',views.staff_home,name='staff_home'),
    path('view_student_applications',views.view_student_applications,name='view_student_applications'),
    path('update_staff_remark/<int:application_id>/', views.update_staff_remark, name='update_staff_remark'),
    path('approval_status_staff_advisor/<int:application_id>/', views.approval_status_staff_advisor, name='approval_status_staff_advisor'),
    path('view_students/', views.view_students_by_department, name='view_students_by_department'),
    path('assign_class_rep/', views.assign_class_rep, name='assign_class_rep'),
    path('add_students/', views.add_student, name='add_students'),
    path('view_feedback/',views.view_feedback, name='view_feedback')


]