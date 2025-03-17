from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from office_admin.models import *
from staff_advisor.models import *
from hod.models import *
from student.models import *
from mainsite.models import *


def admin_home(request):
    application = student_application_request.objects.filter(hod_approval_status='Approved', delete_status=0).count()
    approved_applications=student_application_request.objects.filter(office_approval_status= 'Approved').count()
    print(application)
    return render(request,"office_admin/home.html",{'application':application,'approved_applications':approved_applications})

def office_admin_login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        if office_admin.objects.filter(username=username).exists():
            user_password = office_admin.objects.get(username=username).password
            if user_password == password:
                print('Existing User')
                request.session['user_nme'] = username
                request.session.set_expiry(0)
                return redirect('admin_home')
            else:
                print('Permission Denied By Super Admin, user_status == 0')
                messages.error(request, 'Permission Denied By Super Admin')
                return render(request, 'mguif_admin/login.html')
    return render(request,"office_admin/office_admin_login.html")


def logout_view(request):
    request.session.flush()  # Completely clears the session
    logout(request)  # Logs out the user
    return redirect('office_admin_login')  # Redirect to the login page (update as needed)


def course_config(request):
    if request.method=="POST":
        course_name=request.POST.get('course')
        add=course()
        add.course_name=course_name
        add.save()
        messages.success(request,'Successfully Added')
        return redirect('course_config')
    table=course.objects.filter(delete_status=0)
    context={'table':table}
    return render(request,"office_admin/course_configuration.html",context)


def department_config(request):
    if request.method=='POST':
        select=request.POST.get('select_name')
        branch=request.POST.get('branch')
        obj=departments()
        obj.department_name=branch
        obj.course_pk=course.objects.get(id=select)
        obj.save()
        messages.success(request,'Successfully Added')
        return redirect('department_config')
    cour = course.objects.filter(delete_status=0)
    table = departments.objects.filter(delete_status=0)
    context={'course':cour,'table':table}
    return render(request,"office_admin/department_configuration.html",context)


def department_delete(request):
    if request.method=='POST':
        id=request.POST.get('deletepackageid')
        delete=departments.objects.get(id=id)
        delete.delete_status=1
        delete.save()
        messages.success(request,'Delete Successfully')
        return redirect('department_config')
    
    
def course_delete(request):
    if request.method=='POST':
        id=request.POST.get('deletepackageid')
        delete=course.objects.get(id=id)
        delete.delete_status=1
        delete.save()
        messages.success(request,'Delete Successfully')
        return redirect('course_config')


def add_staff_advisor(request):
  
    try:
        user_nme = request.session.get('user_nme')
        # if user_nme is None:    
        #     return redirect('error_404')
        department = departments.objects.filter(delete_status=0)  # Exclude deleted records
        if request.method == 'POST' and 'add' in request.POST:
            name = request.POST.get('name').strip()
            email = request.POST.get('email').strip()
            password= request.POST.get('password').strip()
            mobile= request.POST.get('mobile').strip()
            department_id=request.POST.get('department')
            # Ensure the department exists before saving
            if department_id:
                department = departments.objects.get(id=department_id)  # Fetch the department object
            else:
                department = None  # Handle cases where no department is selected

              # Check if the email already exists
            if staff_advisor.objects.filter(email=email).exists():
                messages.error(request, 'A staff advisor with this email already exists.')
                return redirect('add_staff_advisor')    
           
            staff = staff_advisor.objects.create(
                    name=name,
                    email=email,
                    password=password,
                    mobile=mobile,
                    is_active=1,
                    department_pk=department 
                    
                )

            # Create login entry for staff advisor
            department_login.objects.create(
                staff_advisor_pk=staff,
                role="staff_advisor",
                delete_status=False
            )

            messages.success(request, 'Successfully saved the staff advisor.')
            return redirect('add_staff_advisor')
        
        # Fetch all data from the database
        all_data = staff_advisor.objects.filter(delete_status=False).order_by('-id')  # Adjust filter as needed

        contexts = {
            'username': user_nme,
            'all_data': all_data,
            'department':department
        }
    
        return render(request,"office_admin/add_staff_advisor.html",contexts)

    except Exception as e:
        print('Exception in staff_advisor:', e)
        messages.error(request, 'An error occurred. Please contact admin.')
        return render(request,"office_admin/add_staff_advisor.html")
    



def edit_staff_advisor(request):
    if request.method == "POST":
        try:
            user_nme = request.session.get('user_nme')
            if user_nme is None:
                return redirect('error_404')
            
            admin_pk = request.POST.get("admin_pk")
            name = request.POST.get("name")
            email = request.POST.get("email")
            password = request.POST.get("password")
            mobile = request.POST.get("mobile")
            department_id=request.POST.get('department')
            # Ensure the department exists before saving
            if department_id:
                department = departments.objects.get(id=department_id)  # Fetch the department object
            else:
                department = None  # Handle cases where no department is selected

            entry = get_object_or_404(staff_advisor, pk=admin_pk)
            entry.name = name
            entry.email = email
            entry.password = password
            entry.mobile = mobile
            entry. department_pk=department 

            entry.save()
            messages.success(request, 'Updated Successfully.')

            return redirect('add_staff_advisor')

        except Exception as e:
            print('Exception in add_staff_advisor:', e)
            messages.error(request, 'An error occurred. Please contact  admin.')
            return render(request,"office_admin/add_staff_advisor.html")

    return redirect('add_staff_advisor')

def delete_staff_advisor(request):
    try:
        user_nme = request.session.get('user_nme')
        if user_nme is None:
            return redirect('error_404')
        
        print("POST data:", request.POST)
        admin_pk = request.POST.get('admin_pk')
        print("Received chat_id_pk:", admin_pk)
        # Check if staff_advisor exists
        main_admin_record = staff_advisor.objects.get(id=admin_pk)
        main_admin_record.delete_status = True
        main_admin_record.save()

        login_record = department_login.objects.filter(staff_advisor_pk=main_admin_record).first()
        if login_record:
            login_record.delete_status = True
            login_record.save()

        messages.success(request, 'Successfully deleted the staff advisor.')
        return redirect('add_staff_advisor')
    except main_admin_record.DoesNotExist:   
        messages.error(request, 'staff_advisor not found.')
        return redirect('add_staff_advisor')
    except Exception as e:
        # Handle other exceptions
        print('Exception delete_staff_advisor:', e)
        messages.error(request, 'An error occurred while deleting the staff_advisor. Please contact  admin.')
      
        return redirect('add_staff_advisor')



def change_admin_status(request, admin_pk):
    if request.method == 'POST':
        try:
          
            admin = get_object_or_404(staff_advisor, pk=admin_pk)
            status = request.POST.get('adminstatus')
            print(admin_pk)

            if status == 'Block':
                admin.is_active = 2  # Set is_active to 2 for blocking
                admin.save()
            if status == 'Allow':
                admin.is_active = 1  # Set is_active 
                admin.save()    
            
            messages.success(request, 'Successfully changed the status')
            return redirect('add_staff_advisor')  # Redirect after successfully updating status

        except Exception as e:
            print('Exception in change_admin_status:', e)
            messages.error(request, 'An error occurred. Please contact  admin.')
            return redirect('add_staff_advisor')  # Redirect to a safe page even on error

    else:
        return redirect('add_staff_advisor')  
    
def add_hod(request) :
    try:
        user_nme = request.session.get('user_nme')
        # if user_nme is None:
        #     return redirect('error_404')
        department = departments.objects.filter(delete_status=0)  # Exclude deleted records
        if request.method == 'POST' and 'add' in request.POST:
            name = request.POST.get('name').strip()
            email = request.POST.get('email').strip()
            password= request.POST.get('password').strip()
            mobile= request.POST.get('mobile').strip()
            department_id=request.POST.get('department')
            # Ensure the department exists before saving
            if department_id:
                department = departments.objects.get(id=department_id)  # Fetch the department object
            else:
                department = None  # Handle cases where no department is selected

              # Check if the email already exists
            if hod.objects.filter(email=email).exists():
                messages.error(request, 'A hod with this email already exists.')
                return redirect('add_hod')    
           
           
            hod_data = hod.objects.create(
                    name=name,
                    email=email,
                    password=password,
                    mobile=mobile,
                    is_active=1,
                    department_pk=department 

                    
                )

            # Create login entry for staff advisor
            department_login.objects.create(
                hod_pk=hod_data,
                role="hod",
                delete_status=False
            )

            messages.success(request, 'Successfully saved the HOD.')
            return redirect('add_hod')
        
        # Fetch all data from the database
        all_data = hod.objects.filter(delete_status=False).order_by('-id')  # Adjust filter as needed

        contexts = {
            'username': user_nme,
            'all_data': all_data,
            'department':department
        }
    
        
        return render(request,'office_admin/add_hod.html',contexts)   

    except Exception as e:
        print('Exception in add_hod:', e)
        messages.error(request, 'An error occurred. Please contact admin.')
        return render(request,'office_admin/add_hod.html')   
    

def edit_hod(request):
    if request.method == "POST":
        try:
            user_nme = request.session.get('user_nme')
            if user_nme is None:
                return redirect('error_404')
            
            admin_pk = request.POST.get("admin_pk")
            name = request.POST.get("name")
            email = request.POST.get("email")
            password = request.POST.get("password")
            mobile = request.POST.get("mobile")
            department_id=request.POST.get('department')
            # Ensure the department exists before saving
            if department_id:
                department = departments.objects.get(id=department_id)  # Fetch the department object
            else:
                department = None  # Handle cases where no department is selected

            entry = get_object_or_404(hod, pk=admin_pk)
            entry.name = name
            entry.email = email
            entry.password = password
            entry.mobile = mobile
            entry. department_pk=department 


            entry.save()
            messages.success(request, 'Updated Successfully.')

            return redirect('add_hod')

        except Exception as e:
            print('Exception in add_hod:', e)
            messages.error(request, 'An error occurred. Please contact  admin.')
            return render(request,"office_admin/add_hod.html")

    return redirect('add_hod')

def delete_hod(request):
    try:
        user_nme = request.session.get('user_nme')
        if user_nme is None:
            return redirect('error_404')
        
        print("POST data:", request.POST)
        admin_pk = request.POST.get('admin_pk')
        print("Received chat_id_pk:", admin_pk)
        main_admin_record = hod.objects.get(id=admin_pk)
        main_admin_record.delete_status = True
        main_admin_record.save()

        login_record = department_login.objects.filter(hod_pk=main_admin_record).first()
        if login_record:
            login_record.delete_status = True
            login_record.save()

        messages.success(request, 'Successfully deleted the hod.')
        return redirect('add_hod')
    except main_admin_record.DoesNotExist:   
        messages.error(request, 'hod not found.')
        return redirect('add_hod')
    except Exception as e:
        # Handle other exceptions
        print('Exception delete_hod:', e)
        messages.error(request, 'An error occurred while deleting the hod. Please contact  admin.')
      
        return redirect('add_hod')



def change_status_hod(request, admin_pk):
    if request.method == 'POST':
        try:
          
            admin = get_object_or_404(hod, pk=admin_pk)
            status = request.POST.get('adminstatus')
            print(admin_pk)

            if status == 'Block':
                admin.is_active = 2  # Set is_active to 2 for blocking
                admin.save()
            if status == 'Allow':
                admin.is_active = 1  # Set is_active 
                admin.save()    
            
            messages.success(request, 'Successfully changed the status')
            return redirect('add_hod')  # Redirect after successfully updating status

        except Exception as e:
            print('Exception in change_admin_status:', e)
            messages.error(request, 'An error occurred. Please contact  admin.')
            return redirect('add_hod')  # Redirect to a safe page even on error

    else:
        return redirect('add_hod')  
    
    
# def feedback_menu(request):
#     if request.method == 'POST':
#         id=request.POST.get('id')
#         # return HttpResponse(id)
#         select=request.POST.get('select_value')
#         update=feedback_enable.objects.get(id=id)
#         update.enable_status=select
#         update.save()
#         messages.success(request, 'Successfully changed the status')
#         return redirect('feedback_menu')
#     ids=1
#     status=feedback_enable.objects.get(id=ids)
#     context={'status':status}
#     return render(request,"office_admin/feed_back_menu.html",context)

def feedback_menu(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        select = request.POST.get('select_value') == '1'  # Convert "1" to True and "0" to False

        update, created = feedback_enable.objects.get_or_create(id=id, defaults={'enable_status': select})

        if not created:  # If record exists, update it
            update.enable_status = select
            update.save()
            messages.success(request, 'Successfully changed the status')
        else:
            messages.success(request, 'New record created successfully')

        return redirect('feedback_menu')

    ids = 1
    status, created = feedback_enable.objects.get_or_create(id=ids, defaults={'enable_status': False})  

    context = {'status': status}
    return render(request, "office_admin/feed_back_menu.html", context)

    
def view_applications(request):
    application_details = student_application_request.objects.filter(hod_approval_status='Approved').order_by('-id')

    return render(request,'office_admin/view_applications.html',{'application_details':application_details})    


from django.core.files.storage import FileSystemStorage

def update_application(request, application_id):
    application_entry = get_object_or_404(student_application_request, id=application_id)

    if request.method == 'POST':
        # office_remark = request.POST.get('office_remark', '')
        office_signature = request.FILES.get('office_signature')

        # Update office remark
        # application_entry.office_remark = office_remark

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

from django.utils.timezone import now


def approval_status_office(request, admin_pk):  
    if request.method == "POST":
        application = get_object_or_404(student_application_request, pk=admin_pk)
        new_status = request.POST.get("adminstatus")  # Get status from form
        remark = request.POST.get("office_remark", "").strip()  # Get remarks

        # Update application status and date
        application.office_approval_status = new_status
        application.office_approval_date = now()
        application.office_remark = remark  # Save remark
        application.save()

        messages.success(request, "Application status updated successfully.")
        return redirect("view_applications")  # Redirect to the applications page

    messages.error(request, "Invalid request.")
    return redirect("view_applications")


def event_config(request):
    if request.method=="POST":
        event_name=request.POST.get('event')
        add=event()
        add.event_name=event_name
        add.save()
        messages.success(request,'Successfully Added')
        return redirect('event_config')
    event_data=event.objects.filter(delete_status=0)
    context={'events':event_data}
    return render(request,"office_admin/event_configuration.html",context)


def event_delete(request):
    if request.method=='POST':
        id=request.POST.get('deletepackageid')
        delete=event.objects.get(id=id)
        delete.delete_status=1
        delete.save()
        messages.success(request,'Delete Successfully')
        return redirect('event_config')
    
#Adding staff incharge
def add_staff_incharge(request):
  
    try:
        user_nme = request.session.get('user_nme')
        # if user_nme is None:    
        #     return redirect('error_404')
        department = departments.objects.filter(delete_status=0)  # Exclude deleted records
        events_data = event.objects.filter(delete_status=0)  # Exclude deleted records
        if request.method == 'POST' and 'add' in request.POST:
            name = request.POST.get('name').strip()
            email = request.POST.get('email').strip()
            password= request.POST.get('password').strip()
            mobile= request.POST.get('mobile').strip()
            department_id=request.POST.get('department')
            events_id=request.POST.get('events')
            # Ensure the department exists before saving
            if department_id:
                department = departments.objects.get(id=department_id)  # Fetch the department object
            else:
                department = None  # Handle cases where no department is selected

            if events_id:
                events_data = event.objects.get(id=events_id)  # Fetch the event object
            else:
                events_data = None  # Handle cases where no event is selected
           
            staff_incharge_data = staff_incharge.objects.create(
                    name=name,
                    email=email,
                    password=password,
                    mobile=mobile,
                    is_active=1,
                    department_pk=department, 
                    event_pk=events_data,
                    
                )

            # Create login entry for staff advisor
            department_login.objects.create(
                staff_incharge_pk=staff_incharge_data,
                role="staff_incharge",
                delete_status=False
            )

            messages.success(request, 'Successfully saved the staff incharge.')
            return redirect('add_staff_incharge')
        
        # Fetch all data from the database
        all_data = staff_incharge.objects.filter(delete_status=False).order_by('-id')  # Adjust filter as needed

        contexts = {
            'username': user_nme,
            'all_data': all_data,
            'department':department,
            'event_data':events_data,
        }
    
        return render(request,"office_admin/add_staff_incharge.html",contexts)

    except Exception as e:
        print('Exception in add_staff_incharge:', e)
        messages.error(request, 'An error occurred. Please contact admin.')
        return render(request,"office_admin/add_staff_incharge.html")
    

def edit_staff_incharge(request):
    if request.method == "POST":
        try:
            user_nme = request.session.get('user_nme')
            if user_nme is None:
                return redirect('error_404')
            
            staff_incharge_pk = request.POST.get("staff_incharge_pk")
            name = request.POST.get("name")
            email = request.POST.get("email")
            password = request.POST.get("password")
            mobile = request.POST.get("mobile")
            department_id=request.POST.get('department')
            event_id=request.POST.get('events')
            # Ensure the department exists before saving
            if department_id:
                department = departments.objects.get(id=department_id)  # Fetch the department object
            else:
                department = None  # Handle cases where no department is selected

            # Ensure the event exists before saving
            if event_id:
                event_data = event.objects.get(id=event_id)  # Fetch the event object
            else:
                event_data = None  # Handle cases where no event is selected

            entry = get_object_or_404(staff_incharge, pk=staff_incharge_pk)
            entry.name = name
            entry.email = email
            entry.password = password
            entry.mobile = mobile 
            entry.department_pk=department
            entry.event_pk=event_data

            entry.save()
            messages.success(request, 'Updated Successfully.')

            return redirect('add_staff_incharge')

        except Exception as e:
            print('Exception in add_staff_incharge:', e)
            messages.error(request, 'An error occurred. Please contact  admin.')
            return render(request,"office_admin/add_staff_incharge.html")

    return redirect('add_staff_incharge')

def delete_staff_incharge(request):
    try:
        user_nme = request.session.get('user_nme')
        if user_nme is None:
            return redirect('error_404')
        
        print("POST data:", request.POST)
        staff_incharge_pk = request.POST.get('staff_incharge_pk')
        # Check if staff_incharge exists
        main_admin_record = staff_incharge.objects.get(id=staff_incharge_pk)
        main_admin_record.delete_status = True
        main_admin_record.save()

        login_record = department_login.objects.filter(staff_incharge_pk=main_admin_record).first()
        if login_record:
            login_record.delete_status = True
            login_record.save()

        messages.success(request, 'Successfully deleted the staff incharge.')
        return redirect('add_staff_incharge')
    except main_admin_record.DoesNotExist:   
        messages.error(request, 'staff_advisor not found.')
        return redirect('add_staff_incharge')
    except Exception as e:
        # Handle other exceptions
        print('Exception delete_staff_incharge:', e)
        messages.error(request, 'An error occurred while deleting the staff_advisor. Please contact  admin.')
      
        return redirect('add_staff_incharge')



def change_staff_incharge_status(request, staff_incharge_pk):
    if request.method == 'POST':
        try:
          
            incharge = get_object_or_404(staff_incharge, pk=staff_incharge_pk)
            status = request.POST.get('incharge_status')
            print(staff_incharge_pk)

            if status == 'Block':
                incharge.is_active = 2  # Set is_active to 2 for blocking
                incharge.save()
            if status == 'Allow':
                incharge.is_active = 1  # Set is_active 
                incharge.save()    
            
            messages.success(request, 'Successfully changed the status')
            return redirect('add_staff_incharge')  # Redirect after successfully updating status

        except Exception as e:
            print('Exception in change_admin_status:', e)
            messages.error(request, 'An error occurred. Please contact  admin.')
            return redirect('add_staff_incharge')  # Redirect to a safe page even on error

    else:
        return redirect('add_staff_incharge')  
    
def feedback_menu(request):
    if request.method == 'POST':
        id=request.POST.get('id')
        # return HttpResponse(id)
        select=request.POST.get('select_value')
        update=feedback_enable.objects.get(id=id)
        update.enable_status=select
        update.save()
        messages.success(request, 'Successfully changed the status')
        return redirect('feedback_menu')
    ids=1
    status=feedback_enable.objects.get(id=ids)
    context={'status':status}
    return render(request,"office_admin/feed_back_menu.html",context)





from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import os
from django.conf import settings


def upload_office_documents(request):
    documents = office_documents.objects.all()
    uploaded_documents = office_documents.objects.filter(document_url__isnull=True) | office_documents.objects.filter(document_url="")

    if request.method == "POST":
        if "delete_document_id" in request.POST:  # Check if delete request
            document_id = request.POST.get("delete_document_id")
            document = get_object_or_404(office_documents, id=document_id)

            # Delete the file from storage
            file_path = os.path.join(settings.MEDIA_ROOT, document.document_url.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete from the database
            document.delete()
            messages.success(request, "Document deleted successfully.")
            return redirect("upload_office_documents")

        # File upload logic
        uploaded_file = request.FILES.get("document_file")
        document_id = request.POST.get("document_id")

        if uploaded_file and document_id:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'documents/'))
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_url = fs.url(os.path.join('documents', filename))

            # Update the document with the uploaded file URL
            document = office_documents.objects.get(id=document_id)
            document.document_url = file_url
            document.save()

            messages.success(request, "Successfully uploaded document.")
            return redirect("upload_office_documents")

    return render(request, "office_admin/office_documents.html", {
    "documents": documents,
    "uploaded_documents": uploaded_documents
     })
