from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/logout/', auth_views.LogoutView.as_view(next_page='admin:login'), name='admin_logout'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('apps.core_app.urls')),
    path('produtos/', include('apps.catalog.urls', namespace='catalog')),
    path('pedidos/', include('apps.orders.urls', namespace='orders')),
    path('planos/', include('apps.plans.urls', namespace='plans')),
    path('fidelidade/', include('apps.loyalty.urls', namespace='loyalty')),
    path('eventos/', include('apps.events.urls', namespace='events')),
    path('minha-conta/', include('apps.accounts.urls', namespace='accounts')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('agendamento/', include('apps.appointments.urls', namespace='appointments')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns