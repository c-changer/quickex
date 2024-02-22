from django.shortcuts import render

# Create your views here.
def partners(request):
    return render(request, "info/partners.html")

def wallet(request):
    return render(request, "info/wallet.html")

def support(request):
    return render(request, "info/support.html")

def aml(request):
    return render(request, "info/aml.html")

def blog(request):
    return render(request, "info/blog.html")
