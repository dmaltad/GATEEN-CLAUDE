from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('estoque/', views.stock_view, name='stock'),
    path('estoque/movimentacao/<int:product_id>/', views.stock_movement_create, name='stock_movement'),
    path('caixa/', views.cash_register_view, name='cash_register'),
    path('pedidos/', views.order_management_view, name='orders'),
    path('pedidos/<int:pk>/status/', views.update_order_status, name='update_order_status'),
]