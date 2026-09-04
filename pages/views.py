from django.shortcuts import render

# Vista que muestra la página principal de bienvenida
def home_view(request):
    return render(request, 'home.html')