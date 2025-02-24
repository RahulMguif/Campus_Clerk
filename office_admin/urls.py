from django.urls import path
from office_admin import views

urlpatterns = [
    path('admin_home/',views.admin_home,name='admin_home')
]