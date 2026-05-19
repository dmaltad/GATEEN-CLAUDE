from django import forms
from django.utils import timezone
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model  = Appointment
        fields = ['pet', 'service', 'scheduled_at', 'notes']
        widgets = {
            'pet':          forms.Select(attrs={'class': 'form-select'}),
            'service':      forms.Select(attrs={'class': 'form-select'}),
            'scheduled_at': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['pet'].queryset = user.pets.all()
        self.fields['scheduled_at'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean_scheduled_at(self):
        from .views import is_valid_slot
        dt = self.cleaned_data.get('scheduled_at')
        if not dt:
            return dt

        now = timezone.now()
        if dt <= now:
            raise forms.ValidationError('O horário deve ser futuro.')

        if not is_valid_slot(dt):
            raise forms.ValidationError(
                'Horário fora do funcionamento: Seg–Sex 07h–17h, Sáb 07h–13h. '
                'Domingos não atendemos.'
            )

        # Verifica conflito de horário (slot de 1h)
        from datetime import timedelta
        slot_end = dt + timedelta(hours=1)
        conflict = Appointment.objects.filter(
            scheduled_at__gte=dt,
            scheduled_at__lt=slot_end,
            status__in=['pending', 'confirmed'],
        ).exists()
        if conflict:
            raise forms.ValidationError('Este horário já está ocupado. Escolha outro.')

        return dt