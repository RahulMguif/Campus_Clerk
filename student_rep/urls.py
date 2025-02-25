from django.urls import path
from student_rep import views

urlpatterns = [
    path('student_rep_home/',views.student_rep_home,name='student_rep_home')
]