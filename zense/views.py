from django.shortcuts import render

def home(request):
    context={
        
    }
    return render(request, "index.html", context)


def temp(request):
    if request.user.is_superuser:
        return render(request, "base1.html", {})