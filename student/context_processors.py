
from office_admin.models import feedback_enable


def feedback_status(request):
    """Returns True if feedback should be shown, otherwise False"""
    return {'feed': feedback_enable.objects.filter(enable_status=1).exists()}


from mainsite.models import student_registration

def student_context(request):
    student_id = request.session.get("student_id")
    student = student_registration.objects.filter(id=student_id).first()
    return {"is_class_rep": student.is_class_rep if student else 0}


# Student email, name and profile pic passingf for global use.
# from mainsite.models import student_registration

# def student_profile(request):
#     if not request.session.get('student_id'):
#         return {}  # Return an empty dictionary if no user is logged in

#     student = student_registration.objects.filter(pk=request.session.get('student_id')).first()
    
#     return {
#         'student_profile_pic': student.profile_pic_url if student and student.profile_pic_url else 'admin/images/faces/avatar.jpg',
#         'student_name': student.fullname if student else '',
#         'student_email': student.email if student else '',
#     }


from .models import student_registration

def student_menu_context(request):
    student_id = request.session.get("student_id")
    student = student_registration.objects.filter(id=student_id).first()
    return {"show_club_menu": student.is_club_coordinator if student else 0}