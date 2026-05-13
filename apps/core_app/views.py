from django.views.generic import TemplateView
from apps.catalog.models import Product, Category
from apps.events.models import Event, Promotion
from apps.plans.models import ServicePlan
from django.utils import timezone


class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['featured_products'] = Product.objects.filter(is_active=True, is_featured=True).select_related('brand', 'category')[:8]
        ctx['categories'] = Category.objects.filter(is_active=True)[:6]
        ctx['upcoming_events'] = Event.objects.filter(is_active=True, start_date__gte=timezone.now()).order_by('start_date')[:3]
        ctx['active_promotions'] = Promotion.objects.filter(is_active=True, start_date__lte=timezone.now(), end_date__gte=timezone.now())[:4]
        ctx['plans'] = ServicePlan.objects.filter(is_active=True).prefetch_related('features')[:3]
        return ctx