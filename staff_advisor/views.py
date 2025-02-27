from django.shortcuts import render, redirect
from staff_advisor.models import *
from django.contrib import messages

# Create your views here.
def staff_home(request):
    return render(request,"staff_advisor/home.html")

def staff_advisor_login(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = staff_advisor.objects.get(email=email)  # Get user based on email
            
            if user.is_active == 2:  # Check if the account is blocked
                messages.error(request, 'Your account has been blocked. Please contact the administrator.')
                return redirect('home')

            if user.password == password:  # Check password
                print('Existing Staff Advisor')
                request.session['username'] = email
                request.session.set_expiry(0)
                return redirect('staff_home')
            else:
                messages.error(request, 'Invalid password.')
                return redirect('home')
        except staff_advisor.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            return redirect('home')

    return render(request, "office_admin/office_admin_login.html")