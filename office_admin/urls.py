from django.urls import path
from office_admin import views

urlpatterns = [
    path('admin_home/',views.admin_home,name='admin_home'),
    path('office_admin_login/',views.office_admin_login,name='office_admin_login'),
    path('logout/',views.logout_view,name='logout'),
    path('course_config/',views.course_config,name='course_config'),
    path('department_config/',views.department_config,name='department_config'),
    path('department_delete',views.department_delete,name='department_delete'),
    path('course_delete',views.course_delete,name='course_delete'),
    path('add_staff_advisor',views.add_staff_advisor,name='add_staff_advisor'),
    path('edit_staff_advisor',views.edit_staff_advisor,name='edit_staff_advisor'),
    path('delete_staff_advisor',views.delete_staff_advisor,name='delete_staff_advisor'),
    path('change_admin_status/<int:admin_pk>/',views.change_admin_status,name='change_admin_status'),
    path('add_hod',views.add_hod,name='add_hod'),
    path('edit_hod',views.edit_hod,name='edit_hod'),
    path('delete_hod',views.delete_hod,name='delete_hod'),
    path('change_status_hod/<int:admin_pk>/',views.change_status_hod,name='change_status_hod'),
    path('feedback_menu/',views.feedback_menu,name='feedback_menu')

]