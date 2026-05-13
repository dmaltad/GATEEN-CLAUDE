from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('carrinho/', views.cart_view, name='cart'),
    path('adicionar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remover/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('atualizar/<int:item_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('meus-pedidos/', views.order_list_view, name='order_list'),
    path('pedido/<int:pk>/', views.order_detail_view, name='order_detail'),
]