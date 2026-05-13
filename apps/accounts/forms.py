from django import forms
from .models import User, Address, Pet


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'birth_date', 'cpf', 'avatar']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['label', 'cep', 'street', 'number', 'complement', 'neighborhood', 'city', 'state', 'is_default']


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'species', 'breed', 'size', 'birth_date', 'photo', 'observations']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }