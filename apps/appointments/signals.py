"""
Notificações por e-mail para agendamentos de banho e tosa.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction as db_transaction

from .models import Appointment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Appointment)
def appointment_notifications(sender, instance, created, **kwargs):
    if created:
        db_transaction.on_commit(lambda: _email_appointment_created(instance))
    else:
        db_transaction.on_commit(lambda: _email_appointment_status(instance, created))


def _email_appointment_created(appt):
    from apps.core_app.email_utils import send_gateen_email
    send_gateen_email(
        to_email      = appt.user.email,
        subject       = f'Agendamento confirmado — {appt.pet.name} 🐾',
        template_name = 'appointment_created',
        context       = {'appt': appt, 'user': appt.user},
    )


def _email_appointment_status(appt, created):
    if created:
        return
    # Só envia para mudanças relevantes
    if appt.status not in ('confirmed', 'done', 'cancelled'):
        return
    from apps.core_app.email_utils import send_gateen_email
    send_gateen_email(
        to_email      = appt.user.email,
        subject       = f'Agendamento de {appt.pet.name} — {appt.get_status_display()}',
        template_name = 'appointment_status_changed',
        context       = {'appt': appt, 'user': appt.user},
    )