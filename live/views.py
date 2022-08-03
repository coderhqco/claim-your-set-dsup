from django.shortcuts import render, HttpResponse

# Create your views here.

def liveUpdate(request):
    return render(request,"live/index.html")