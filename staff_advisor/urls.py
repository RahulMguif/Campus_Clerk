from django.urls import path
from staff_advisor import views

urlpatterns = [
    path('staff_home/',views.staff_home,name='staff_home'),
    path('view_student_applications',views.view_student_applications,name='view_student_applications'),
    path('staff_advisor_review_application/<int:application_id>/', views.staff_advisor_review_application, name='staff_advisor_review_application'),
]