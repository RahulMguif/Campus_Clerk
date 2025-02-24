from django.urls import path
from student import views

urlpatterns = [
    path('student_dashboard/', views.student_home, name='student_dashboard'),
    path('student_application/', views.application_form, name='student_application'),
]