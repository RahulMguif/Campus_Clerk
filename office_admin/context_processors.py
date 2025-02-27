from office_admin.models import feedback_enable


def feedback_status(request):
    """Returns True if feedback should be shown, otherwise False"""
    return {'feed': feedback_enable.objects.filter(enable_status=1).exists()}