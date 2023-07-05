from django.urls import path
from .views import generate_certificate, home, about

urlpatterns = [
    path('', home, name='home'),
    path('/about', about, name='about'),
    path('generate-certificate/', generate_certificate, name='generate_certificate'),
]
