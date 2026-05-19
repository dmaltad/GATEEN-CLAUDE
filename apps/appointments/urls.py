from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('agendar/',       views.appointment_booking, name='booking'),
    path('meus/',          views.my_appointments,     name='my_appointments'),
    path('<int:pk>/cancelar/', views.cancel_appointment, name='cancel'),
]