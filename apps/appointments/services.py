"""
Serviço de agendamento: encapsula criação, cancelamento
e regras de desconto de sessão do UserPlan.
"""
from django.utils import timezone
from .models import Appointment


def create_appointment(user, pet, service, scheduled_at, notes=''):
    """
    Cria um agendamento aplicando automaticamente o plano ativo do pet/usuário.
    Retorna (appointment, used_plan: bool, plan_or_None).
    """
    active_plan = _get_active_plan(user)
    used_plan   = False

    appt = Appointment(
        user         = user,
        pet          = pet,
        service      = service,
        scheduled_at = scheduled_at,
        notes        = notes,
        status       = 'pending',
    )

    if active_plan and active_plan.grooming_sessions_remaining > 0:
        appt.user_plan        = active_plan
        appt.used_plan_session = True
        used_plan              = True

    appt.save()

    if used_plan:
        active_plan.grooming_sessions_used += 1
        active_plan.save(update_fields=['grooming_sessions_used'])

    return appt, used_plan, active_plan if used_plan else None


def cancel_appointment(appointment):
    """
    Cancela um agendamento e devolve a sessão ao plano, se aplicável.
    Retorna True se cancelado com sucesso.
    """
    if appointment.status not in ('pending', 'confirmed'):
        return False
    if not appointment.is_upcoming:
        return False

    if appointment.used_plan_session and appointment.user_plan:
        plan = appointment.user_plan
        if plan.grooming_sessions_used > 0:
            plan.grooming_sessions_used -= 1
            plan.save(update_fields=['grooming_sessions_used'])

    appointment.status = 'cancelled'
    appointment.save(update_fields=['status'])
    return True


def _get_active_plan(user):
    try:
        from apps.plans.models import UserPlan
        return (
            UserPlan.objects
            .filter(user=user, status='active')
            .select_related('plan')
            .first()
        )
    except Exception:
        return None