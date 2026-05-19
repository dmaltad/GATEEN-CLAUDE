from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, datetime, timedelta, time

from .models import Appointment
from .forms  import AppointmentForm
from .services import create_appointment, cancel_appointment as svc_cancel


# ── Regras de disponibilidade ─────────────────────────────────

WEEKDAY_HOURS = {
    0: (7, 17),
    1: (7, 17),
    2: (7, 17),
    3: (7, 17),
    4: (7, 17),
    5: (7, 13),
}

SLOT_DURATION = 60


def is_valid_slot(dt: datetime) -> bool:
    weekday = dt.weekday()
    if weekday not in WEEKDAY_HOURS:
        return False
    start_h, end_h = WEEKDAY_HOURS[weekday]
    return start_h <= dt.hour < end_h


def generate_slots(for_date: date):
    weekday = for_date.weekday()
    if weekday not in WEEKDAY_HOURS:
        return []

    start_h, end_h = WEEKDAY_HOURS[weekday]

    booked_hours = set(
        Appointment.objects.filter(
            scheduled_at__date=for_date,
            status__in=['pending', 'confirmed'],
        ).values_list('scheduled_at__hour', flat=True)
    )

    now   = timezone.now()
    slots = []
    h     = start_h

    while h < end_h:
        slot_dt = timezone.make_aware(datetime.combine(for_date, time(h, 0)))
        slots.append({
            'time':   slot_dt,
            'label':  f'{h:02d}:00',
            'booked': h in booked_hours,
            'past':   slot_dt <= now,
        })
        h += 1

    return slots


def build_week(base_date: date):
    return [
        {
            'date':    base_date + timedelta(days=i),
            'slots':   generate_slots(base_date + timedelta(days=i)),
            'is_open': (base_date + timedelta(days=i)).weekday() in WEEKDAY_HOURS,
        }
        for i in range(7)
    ]


# ── Views ─────────────────────────────────────────────────────

@login_required
def appointment_booking(request):
    today       = timezone.localdate()
    week_offset = int(request.GET.get('week', 0))
    base_date   = today + timedelta(weeks=week_offset)
    base_date  -= timedelta(days=base_date.weekday())
    week_days   = build_week(base_date)

    from .services import _get_active_plan
    active_plan = _get_active_plan(request.user)

    preselected = request.GET.get('slot', '')
    form = AppointmentForm(
        user=request.user,
        initial={'scheduled_at': preselected} if preselected else {},
    )

    if request.method == 'POST':
        form = AppointmentForm(user=request.user, data=request.POST)
        if form.is_valid():
            cd  = form.cleaned_data
            appt, used_plan, plan = create_appointment(
                user         = request.user,
                pet          = cd['pet'],
                service      = cd['service'],
                scheduled_at = cd['scheduled_at'],
                notes        = cd.get('notes', ''),
            )

            msg = (
                f'Agendamento de {appt.get_service_display()} para '
                f'{appt.pet.name} em '
                f'{appt.scheduled_at.strftime("%d/%m/%Y às %H:%M")} confirmado! 🐾'
            )
            if used_plan:
                msg += f' (1 sessão descontada do {plan.plan.name})'

            messages.success(request, msg)
            return redirect('appointments:my_appointments')

    my_upcoming = Appointment.objects.filter(
        user=request.user,
        status__in=['pending', 'confirmed'],
        scheduled_at__gte=timezone.now(),
    ).select_related('pet')[:5]

    return render(request, 'appointments/booking.html', {
        'form':        form,
        'week_days':   week_days,
        'week_offset': week_offset,
        'prev_week':   week_offset - 1,
        'next_week':   week_offset + 1,
        'base_date':   base_date,
        'active_plan': active_plan,
        'my_upcoming': my_upcoming,
        'today':       today,
    })


@login_required
def my_appointments(request):
    upcoming = Appointment.objects.filter(
        user=request.user,
        scheduled_at__gte=timezone.now(),
    ).select_related('pet', 'user_plan__plan').order_by('scheduled_at')

    past = Appointment.objects.filter(
        user=request.user,
        scheduled_at__lt=timezone.now(),
    ).select_related('pet').order_by('-scheduled_at')[:15]

    return render(request, 'appointments/my_appointments.html', {
        'upcoming': upcoming,
        'past':     past,
    })


@login_required
def cancel_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, user=request.user)
    if request.method == 'POST':
        ok = svc_cancel(appt)
        if ok:
            messages.success(request, 'Agendamento cancelado.')
        else:
            messages.error(request, 'Este agendamento não pode ser cancelado.')
    return redirect('appointments:my_appointments')