from django.shortcuts import render,redirect, get_object_or_404
from student.models import *
from django.core.files.storage import FileSystemStorage
from django.contrib import messages

# Create your views here.
def hod_home(request):
    return render(request,"hod/home.html")

def review_application(request):
    applications=student_application_request.objects.filter(staff_approval_status ='Approved')
    return render(request,"hod/review_application.html",{'applications':applications})


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