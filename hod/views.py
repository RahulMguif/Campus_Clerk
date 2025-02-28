from django.shortcuts import render,redirect, get_object_or_404
from student.models import *
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.utils.timezone import now

# Create your views here.
def hod_home(request):
    return render(request,"hod/home.html")


def review_application(request):
    # Get the logged-in HOD's email from session
    hod_email = request.session.get('username')

    if not hod_email:
        messages.error(request, "Session expired or user not logged in.")
        return redirect('department_user_login')

    # Get HOD's department details
    try:
        hod_instance = hod.objects.get(email=hod_email)
        department_instance = departments.objects.get(id=hod_instance.department_pk_id)
    except (hod.DoesNotExist, departments.DoesNotExist):
        messages.error(request, "HOD or department details not found.")
        return redirect('department_user_login')

    # Debugging to check department details
    print("HOD Email:", hod_email)
    print("HOD Department ID:", hod_instance.department_pk_id)
    print("HOD Department Name:", department_instance.department_name)

    # Fetch applications for the department
    applications = student_application_request.objects.filter(
        staff_approval_status='Approved',
        branch=department_instance.department_name  # Match by department name, not ID
    )

    print("Filtered Applications:", applications)  # Debugging
    applications = list(applications) 

    return render(request, "hod/review_application.html", {'applications': applications})


def update_application_hod(request, application_id):
    application_entries = get_object_or_404(student_application_request, id=application_id)

    if request.method == 'POST':
        hod_remark = request.POST.get('hod_remark', '')
        hod_signature = request.FILES.get('hod_signature')

        # Update office remark
        application_entries.hod_remark = hod_remark

        # Handle office signature file upload
        if hod_signature:
            fs = FileSystemStorage(location='media/hod_signature/')
            filename = fs.save(hod_signature.name, hod_signature)
            application_entries.hod_signature_url = f'media/hod_signature/{filename}'

        # Save changes
        application_entries.save()
        print("saved application")
        messages.success(request, "Application updated successfully!")
        return redirect('review_application')  # Adjust based on your URL name

    return render(request, 'hod/review_application.html', {'application_entries': application_entries})





def approval_status_hod(request, application_pk):  
    if request.method == "POST":
        application = get_object_or_404(student_application_request, pk=application_pk)
        new_status = request.POST.get("adminstatus")  # Get status from form

        # Update application status and date
        application.hod_approval_status = new_status
        application.hod_approval_date = now()
        application.save()

        messages.success(request, "Application status updated successfully.")
        return redirect("review_application")  # Redirect to the applications page

    messages.error(request, "Invalid request.")
    return redirect("review_application")