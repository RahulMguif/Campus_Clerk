from django.urls import path
from office_admin import views

urlpatterns = [
    path('admin_home/',views.admin_home,name='admin_home'),
    path('office_admin_login/',views.office_admin_login,name='office_admin_login'),
    path('logout/',views.logout_view,name='logout'),
    path('course_config/',views.course_config,name='course_config'),
    path('department_config/',views.department_config,name='department_config'),
    path('department_delete',views.department_delete,name='department_delete'),
    path('course_delete',views.course_delete,name='course_delete')
]