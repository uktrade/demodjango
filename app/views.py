from django.http import HttpResponse


def index(request):
    return HttpResponse("We have a working site")
