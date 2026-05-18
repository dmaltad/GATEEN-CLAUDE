from django.urls import path
from . import views_management as mgmt

app_name = 'dashboard'

urlpatterns = [
    # Dashboard home
    path('', mgmt.dashboard_home, name='home'),

    # ── Gestão de Produtos ──────────────────────────────
    path('gestao/produtos/',                     mgmt.product_list,      name='product_list'),
    path('gestao/produtos/novo/',                mgmt.product_create,    name='product_create'),
    path('gestao/produtos/<int:pk>/editar/',     mgmt.product_edit,      name='product_edit'),
    path('gestao/produtos/<int:pk>/excluir/',    mgmt.product_delete,    name='product_delete'),

    # ── Gestão de Pedidos ───────────────────────────────
    path('gestao/pedidos/',                          mgmt.order_list_staff,   name='order_list_staff'),
    path('gestao/pedidos/<str:order_number>/',       mgmt.order_detail_staff, name='order_detail_staff'),

    # ── Gestão de Eventos ───────────────────────────────
    path('gestao/eventos/',                    mgmt.event_list,   name='event_list'),
    path('gestao/eventos/novo/',               mgmt.event_create, name='event_create'),
    path('gestao/eventos/<int:pk>/editar/',    mgmt.event_edit,   name='event_edit'),

    # ── Gestão de Planos ────────────────────────────────
    path('gestao/planos/',                mgmt.plan_list,     name='plan_list'),
    path('gestao/planos/ativos/',         mgmt.userplan_list, name='userplan_list'),

    # ── Gestão de Fidelidade ────────────────────────────
    path('gestao/fidelidade/',            mgmt.loyalty_list,  name='loyalty_list'),

    # ── Gestão de Usuários ──────────────────────────────
    path('gestao/usuarios/',                    mgmt.user_list,  name='user_list'),
    path('gestao/usuarios/<int:pk>/editar/',    mgmt.user_edit,  name='user_edit'),
    path('gestao/cargos/',                      mgmt.group_list, name='group_list'),
]