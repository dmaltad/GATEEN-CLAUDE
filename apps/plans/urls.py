from django.urls import path
from . import views

app_name = 'plans'

urlpatterns = [
    path('', views.PlanListView.as_view(), name='plan_list'),
    path('<slug:slug>/assinar/', views.subscribe_plan, name='subscribe'),
]