from django.shortcuts import render, redirect, get_object_or_404
from staff_advisor.models import *
from django.contrib import messages
from student.models import *
from django.core.files.storage import FileSystemStorage

# Create your views here.
def staff_home(request):
    return render(request,"staff_advisor/home.html")

def view_student_applications(request):
    application_details = student_application_request.objects.all()
    return render(request,'staff_advisor/view_student_applications.html',{'application_details':application_details})    



def staff_advisor_review_application(request, application_id):
    application_entry = get_object_or_404(student_application_request, id=application_id)

    if request.method == 'POST':
        office_remark = request.POST.get('office_remark', '')
        office_signature = request.FILES.get('office_signature')

        # Update office remark
        application_entry.office_remark = office_remark

        # Handle office signature file upload
        if office_signature:
            fs = FileSystemStorage(location='media/office_signatures/')
            filename = fs.save(office_signature.name, office_signature)
            application_entry.office_signature_url = f'media/office_signatures/{filename}'

        # Save changes
        application_entry.save()
        print("saved application")
        messages.success(request, "Application updated successfully!")
        return redirect('view_applications')  # Adjust based on your URL name

    return render(request, 'office_admin/update_application.html', {'application_entry': application_entry})