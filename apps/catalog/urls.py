from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('categoria/<slug:category_slug>/', views.ProductListView.as_view(), name='by_category'),
    path('marca/<slug:brand_slug>/', views.ProductListView.as_view(), name='by_brand'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]