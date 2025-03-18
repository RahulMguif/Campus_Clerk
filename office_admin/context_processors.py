from office_admin.models import feedback_enable


def feedback_status(request):
    """Returns True if feedback should be shown, otherwise False"""
    return {'feed': feedback_enable.objects.filter(enable_status=1).exists()}



from mainsite.models import student_registration

def student_menu_context(request):
    student_id = request.session.get("student_id")
    student = student_registration.objects.filter(id=student_id).first()
    return {"show_club_menu": student.is_club_coordinator if student else 0}