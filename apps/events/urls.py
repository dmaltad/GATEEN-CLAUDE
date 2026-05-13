from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListView.as_view(), name='event_list'),
    path('promocoes/', views.PromotionListView.as_view(), name='promotion_list'),  # ANTES do slug
    path('<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
]