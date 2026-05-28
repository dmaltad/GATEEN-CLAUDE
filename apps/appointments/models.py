from django.db import models
from django.utils import timezone


class Appointment(models.Model):
    SERVICE_CHOICES = [
        ('bath',      'Banho'),
        ('grooming',  'Tosa'),
        ('bath_grooming', 'Banho + Tosa'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pendente'),
        ('confirmed', 'Confirmado'),
        ('done',      'Concluído'),
        ('cancelled', 'Cancelado'),
    ]

    user       = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT,
        related_name='appointments', verbose_name='Cliente'
    )
    pet        = models.ForeignKey(
        'accounts.Pet', on_delete=models.PROTECT,
        related_name='appointments', verbose_name='Pet'
    )
    user_plan  = models.ForeignKey(
        'plans.UserPlan', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='appointments', verbose_name='Plano utilizado'
    )

    service      = models.CharField(max_length=20, choices=SERVICE_CHOICES, verbose_name='Serviço')
    scheduled_at = models.DateTimeField(verbose_name='Data e horário')
    status       = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    used_plan_session = models.BooleanField(default=False, verbose_name='Descontou sessão do plano')
    notes        = models.TextField(blank=True, verbose_name='Observações')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['scheduled_at']

    def __str__(self):
        return (
            f'{self.pet.name} — {self.get_service_display()} '
            f'em {self.scheduled_at.strftime("%d/%m/%Y %H:%M")}'
        )

    @property
    def is_upcoming(self):
        return self.scheduled_at > timezone.now()
    
    reminder_sent = models.BooleanField(
        default=False, verbose_name='Lembrete enviado'
    )