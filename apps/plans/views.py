from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import ServicePlan, UserPlan


class PlanListView(ListView):
    model = ServicePlan
    template_name = 'plans/plan_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return ServicePlan.objects.filter(is_active=True).prefetch_related('features')


@login_required
def subscribe_plan(request, slug):
    plan = get_object_or_404(ServicePlan, slug=slug, is_active=True)
    active_plan = UserPlan.objects.filter(user=request.user, status='active').first()

    if request.method == 'POST':
        pet_id = request.POST.get('pet_id')
        pet = None
        if pet_id:
            from apps.accounts.models import Pet
            pet = get_object_or_404(Pet, pk=pet_id, owner=request.user)

        UserPlan.objects.create(
            user=request.user,
            plan=plan,
            pet=pet,
            status='active',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
        )
        messages.success(request, f'Plano {plan.name} contratado com sucesso!')
        return redirect('accounts:profile')

    return render(request, 'plans/subscribe.html', {
        'plan': plan,
        'active_plan': active_plan,
        'pets': request.user.pets.all(),
    })