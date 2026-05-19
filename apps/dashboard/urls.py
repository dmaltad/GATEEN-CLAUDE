from django.urls import path
from . import views_management as mgmt

app_name = 'dashboard'

urlpatterns = [
    path('', mgmt.dashboard_home, name='home'),

    # ── Produtos ────────────────────────────────────────
    path('gestao/produtos/',                     mgmt.product_list,    name='product_list'),
    path('gestao/produtos/novo/',                mgmt.product_create,  name='product_create'),
    path('gestao/produtos/<int:pk>/editar/',     mgmt.product_edit,    name='product_edit'),
    path('gestao/produtos/<int:pk>/excluir/',    mgmt.product_delete,  name='product_delete'),

    # ── Categorias ──────────────────────────────────────
    path('gestao/categorias/',                   mgmt.category_list,   name='category_list'),
    path('gestao/categorias/nova/',              mgmt.category_create, name='category_create'),
    path('gestao/categorias/<int:pk>/editar/',   mgmt.category_edit,   name='category_edit'),
    path('gestao/categorias/<int:pk>/excluir/',  mgmt.category_delete, name='category_delete'),

    # ── Pedidos ─────────────────────────────────────────
    path('gestao/pedidos/',                        mgmt.order_list_staff,   name='order_list_staff'),
    path('gestao/pedidos/<str:order_number>/',     mgmt.order_detail_staff, name='order_detail_staff'),

    # ── Eventos ─────────────────────────────────────────
    path('gestao/eventos/',                  mgmt.event_list,   name='event_list'),
    path('gestao/eventos/novo/',             mgmt.event_create, name='event_create'),
    path('gestao/eventos/<int:pk>/editar/',  mgmt.event_edit,   name='event_edit'),

    # ── Planos ──────────────────────────────────────────
    path('gestao/planos/',                   mgmt.plan_list,     name='plan_list'),
    path('gestao/planos/novo/',              mgmt.plan_create,   name='plan_create'),
    path('gestao/planos/<int:pk>/editar/',   mgmt.plan_edit,     name='plan_edit'),
    path('gestao/planos/<int:pk>/excluir/',  mgmt.plan_delete,   name='plan_delete'),
    path('gestao/planos/ativos/',            mgmt.userplan_list, name='userplan_list'),

    # ── Fidelidade ──────────────────────────────────────
    path('gestao/fidelidade/',                         mgmt.loyalty_list,        name='loyalty_list'),
    path('gestao/fidelidade/regras/',                  mgmt.loyalty_rule_list,   name='loyalty_rule_list'),
    path('gestao/fidelidade/regras/nova/',             mgmt.loyalty_rule_create, name='loyalty_rule_create'),
    path('gestao/fidelidade/regras/<int:pk>/editar/',  mgmt.loyalty_rule_edit,   name='loyalty_rule_edit'),
    path('gestao/fidelidade/regras/<int:pk>/excluir/', mgmt.loyalty_rule_delete, name='loyalty_rule_delete'),

    # ── Usuários ─────────────────────────────────────────
    path('gestao/usuarios/',                  mgmt.user_list,  name='user_list'),
    path('gestao/usuarios/<int:pk>/editar/',  mgmt.user_edit,  name='user_edit'),
    path('gestao/cargos/',                    mgmt.group_list, name='group_list'),

    # ── Agendamentos ─────────────────────────────────────
    path('gestao/agendamentos/',                        mgmt.appointment_list_staff,   name='appointment_list_staff'),
    path('gestao/agendamentos/<int:pk>/status/',        mgmt.appointment_update_status, name='appointment_update_status'),
]