from django.http import HttpResponse

def home(request):
    return HttpResponse("Hostel Management System Running ✅")
