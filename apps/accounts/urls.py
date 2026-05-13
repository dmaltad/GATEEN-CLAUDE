from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('perfil/', views.profile_view, name='profile'),
    path('perfil/editar/', views.edit_profile, name='edit_profile'),
    path('enderecos/novo/', views.add_address, name='add_address'),
    path('pets/novo/', views.add_pet, name='add_pet'),
]