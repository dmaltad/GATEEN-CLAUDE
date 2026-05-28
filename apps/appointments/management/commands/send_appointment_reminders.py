"""
Envia lembretes 1 hora antes do agendamento de banho e tosa.
Execute via cron a cada 5 minutos:
  */5 * * * * cd /path/to/project && python manage.py send_appointment_reminders
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Envia lembretes de agendamento 1 hora antes do horário marcado.'

    def handle(self, *args, **kwargs):
        from apps.appointments.models import Appointment
        from apps.core_app.email_utils import send_gateen_email

        now      = timezone.now()
        # Janela: entre 55 e 65 minutos no futuro (evita duplicatas ao rodar a cada 5 min)
        window_start = now + timedelta(minutes=55)
        window_end   = now + timedelta(minutes=65)

        appts = Appointment.objects.filter(
            scheduled_at__gte=window_start,
            scheduled_at__lte=window_end,
            status__in=['pending', 'confirmed'],
            reminder_sent=False,
        ).select_related('user', 'pet')

        sent = 0
        for appt in appts:
            ok = send_gateen_email(
                to_email      = appt.user.email,
                subject       = f'Lembrete: banho de {appt.pet.name} em 1 hora! ✂️',
                template_name = 'appointment_reminder',
                context       = {'appt': appt, 'user': appt.user},
            )
            if ok:
                appt.reminder_sent = True
                appt.save(update_fields=['reminder_sent'])
                sent += 1

        self.stdout.write(
            self.style.SUCCESS(f'✅ {sent} lembrete(s) enviado(s).')
        )