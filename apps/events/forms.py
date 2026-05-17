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
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 'type': 'datetime-local',
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 'type': 'datetime-local',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Local',
            }),
            'online_link': forms.URLInput(attrs={
                'class': 'form-control', 'placeholder': 'https://',
            }),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'is_online':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

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