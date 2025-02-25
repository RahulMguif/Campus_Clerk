from django.urls import path
from mainsite import views

urlpatterns = [
    path('', views.home_view,name='home'),
    path('login/',views.login,name='login'),
    path('registration/',views.registration,name='registration'),
    path('check-user-existence/', views.check_user_existence, name='check_user_existence'),
]