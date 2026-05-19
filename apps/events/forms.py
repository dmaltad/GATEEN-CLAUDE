from django import forms
from django.utils.text import slugify
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'event_type',
            'description', 'short_description',
            'image', 'banner',
            'start_date', 'end_date',
            'location', 'is_online', 'online_link',
            'is_active', 'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título do evento',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
            }),
            # format corrigido: sem segundos, compatível com datetime-local
            'start_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'end_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Local',
            }),
            'online_link': forms.URLInput(attrs={
                'class': 'form-control', 'placeholder': 'https://',
            }),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            # Checkboxes: SEM class form-control para evitar o bug do CSS
            'is_online':   forms.CheckboxInput(),
            'is_active':   forms.CheckboxInput(),
            'is_featured': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garante que o input datetime-local receba o valor formatado corretamente
        self.fields['start_date'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
        self.fields['end_date'].input_formats   = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']

    def save(self, commit=True):
        event = super().save(commit=False)
        if not event.slug:
            event.slug = slugify(event.title)
        from .models import Event as E
        base, n = event.slug, 1
        while E.objects.filter(slug=event.slug).exclude(pk=event.pk).exists():
            event.slug = f'{base}-{n}'
            n += 1
        if commit:
            event.save()
        return event