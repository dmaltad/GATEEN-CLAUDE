from django.shortcuts import redirect
from django.views.generic import TemplateView
from apps.catalog.models import Product, Category
from apps.events.models import Event, Promotion
from apps.plans.models import ServicePlan
from django.utils import timezone


class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('dashboard:home')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        from django.db.models import Q
        ctx = super().get_context_data(**kwargs)
        ctx['featured_products'] = Product.objects.filter(
            is_active=True,
            is_featured=True,
        ).exclude(
            Q(stock__isnull=True) | Q(stock__quantity__lte=0)
        ).select_related('brand', 'category', 'stock')[:8]

        ctx['categories']    = Category.objects.filter(is_active=True)[:6]
        ctx['plans']         = ServicePlan.objects.filter(
            is_active=True
        ).prefetch_related('features')[:3]
        ctx['upcoming_events'] = Event.objects.filter(
            is_active=True,
            start_date__gte=timezone.now()
        ).order_by('start_date')[:3]
        return ctx