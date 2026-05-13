from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import Event, Promotion


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(is_active=True, start_date__gte=timezone.now()).order_by('start_date')


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'


class PromotionListView(ListView):
    model = Promotion
    template_name = 'events/promotion_list.html'
    context_object_name = 'promotions'

    def get_queryset(self):
        now = timezone.now()
        return Promotion.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now)