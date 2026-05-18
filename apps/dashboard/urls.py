from django.urls import path
from . import views
from . import views_management as mgmt

app_name = 'dashboard'

urlpatterns = [
    # Dashboard home
    path('', views.dashboard_home, name='home'),
    path('estoque/', views.stock_view, name='stock'),
    path('caixa/', views.cash_register_view, name='cash_register'),
    path('pedidos/', views.orders_view, name='orders'),

    # Rota de atualização de status — dois nomes para a mesma view (compatibilidade de templates)
    path('pedidos/<str:order_number>/', views.order_detail_staff_redirect, name='update_order'),
    path('pedidos/<str:order_number>/status/', views.order_detail_staff_redirect, name='update_order_status'),

    # ── Gestão personalizada ──────────────────────────────
    # Produtos
    path('gestao/produtos/',                     mgmt.product_list,    name='product_list'),
    path('gestao/produtos/novo/',                mgmt.product_create,  name='product_create'),
    path('gestao/produtos/<int:pk>/editar/',     mgmt.product_edit,    name='product_edit'),
    path('gestao/produtos/<int:pk>/excluir/',    mgmt.product_delete,  name='product_delete'),

    # Pedidos
    path('gestao/pedidos/',                          mgmt.order_list_staff,   name='order_list_staff'),
    path('gestao/pedidos/<str:order_number>/',       mgmt.order_detail_staff, name='order_detail_staff'),

    # Eventos
    path('gestao/eventos/',                    mgmt.event_list,   name='event_list'),
    path('gestao/eventos/novo/',               mgmt.event_create, name='event_create'),
    path('gestao/eventos/<int:pk>/editar/',    mgmt.event_edit,   name='event_edit'),

    # Planos
    path('gestao/planos/',                mgmt.plan_list,     name='plan_list'),
    path('gestao/planos/ativos/',         mgmt.userplan_list, name='userplan_list'),

    # Fidelidade
    path('gestao/fidelidade/',            mgmt.loyalty_list,  name='loyalty_list'),

    # Usuários
    path('gestao/usuarios/',                    mgmt.user_list,  name='user_list'),
    path('gestao/usuarios/<int:pk>/editar/',    mgmt.user_edit,  name='user_edit'),
    path('gestao/cargos/',                      mgmt.group_list, name='group_list'),
]