from django.shortcuts import render

def home_view(request):
    return render(request, "pages/home.html")

def menu_view(request):
    return render(request, "pages/menu.html")

def bestellen_view(request):
    return render(request, "pages/bestellen.html")
