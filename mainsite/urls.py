from django.urls import path
from mainsite import views

urlpatterns = [
    path('', views.home_view,name='home'),
    path('login/',views.login,name='login'),
    path('registration/',views.registration,name='registration'),
    path('check-user-existence/', views.check_user_existence, name='check_user_existence'),
    path('logout/',views.user_logout,name='student_logout'),
    path('department_user_login/',views.department_user_login,name='department_user_login'),
]