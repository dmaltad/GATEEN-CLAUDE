import re
from django import forms
from django.core.exceptions import ValidationError
from .models import User, Address, Pet

def validate_cpf(cpf: str) -> str:
    """
    Valida CPF matematicamente (algoritmo oficial).
    Retorna o CPF limpo (só dígitos) se válido.
    Levanta ValidationError se inválido.
    """
    cpf_digits = re.sub(r'\D', '', cpf)

    if len(cpf_digits) != 11:
        raise ValidationError('CPF deve ter 11 dígitos.')

    # Rejeita sequências iguais (ex: 111.111.111-11)
    if len(set(cpf_digits)) == 1:
        raise ValidationError('CPF inválido.')

    # Primeiro dígito verificador
    total = sum(int(cpf_digits[i]) * (10 - i) for i in range(9))
    r1 = (total * 10 % 11) % 10
    if r1 != int(cpf_digits[9]):
        raise ValidationError('CPF inválido.')

    # Segundo dígito verificador
    total = sum(int(cpf_digits[i]) * (11 - i) for i in range(10))
    r2 = (total * 10 % 11) % 10
    if r2 != int(cpf_digits[10]):
        raise ValidationError('CPF inválido.')

    return cpf_digits


class CustomSignupForm(forms.Form):
    """
    Formulário customizado para o allauth (sem herdar do SignupForm para evitar import circular).
    """

    first_name = forms.CharField(
        label='Nome',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Seu nome',
            'autocomplete': 'given-name',
        }),
        error_messages={'required': 'Por favor, informe seu nome.'},
    )

    last_name = forms.CharField(
        label='Sobrenome',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Seu sobrenome',
            'autocomplete': 'family-name',
        }),
        error_messages={'required': 'Por favor, informe seu sobrenome.'},
    )

    phone = forms.CharField(
        label='Telefone / WhatsApp',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '(00) 00000-0000',
            'autocomplete': 'tel',
            'inputmode': 'tel',
        }),
    )

    birth_date = forms.DateField(
        label='Data de Nascimento',
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'max': '2010-12-31',   # >= 13 anos
        }),
    )

    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '000.000.000-00',
            'inputmode': 'numeric',
            'autocomplete': 'off',
        }),
    )

    email2 = forms.EmailField(
        label='Confirmar E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Repita seu e-mail',
            'autocomplete': 'email',
        }),
        error_messages={'required': 'Por favor, confirme seu e-mail.'},
    )

    # A ordem dos campos. O allauth injeta email e senhas automaticamente.
    field_order = ['first_name', 'last_name', 'phone', 'birth_date', 'cpf', 'email2']

    # ── Validações individuais ────────────────────────────────

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '').strip()
        if not cpf:
            return ''
        cleaned = validate_cpf(cpf)
        # Verifica unicidade
        if User.objects.filter(cpf=cleaned).exists():
            raise ValidationError('Já existe uma conta com este CPF.')
        return cleaned

    def clean_birth_date(self):
        bd = self.cleaned_data.get('birth_date')
        if bd:
            from django.utils import timezone
            today = timezone.now().date()
            age = (today - bd).days // 365
            if age < 13:
                raise ValidationError('Você precisa ter pelo menos 13 anos para se cadastrar.')
            if age > 120:
                raise ValidationError('Data de nascimento inválida.')
        return bd

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name', '').strip()
        if len(name) < 2:
            raise ValidationError('Nome muito curto.')
        return name.title()

    def clean_last_name(self):
        name = self.cleaned_data.get('last_name', '').strip()
        if len(name) < 2:
            raise ValidationError('Sobrenome muito curto.')
        return name.title()

    def clean(self):
            cleaned_data = super().clean()
            email1 = self.data.get('email', '').strip().lower()
            email2 = cleaned_data.get('email2', '').strip().lower()
            if email1 and email2 and email1 != email2:
                self.add_error('email2', 'Os e-mails não coincidem. Verifique e tente novamente.')
            return cleaned_data

    # ── Salva campos extras no User ───────────────────────────

    def signup(self, request, user):
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name  = self.cleaned_data.get('last_name', '')
        user.phone      = self.cleaned_data.get('phone', '')
        user.birth_date = self.cleaned_data.get('birth_date')
        user.cpf        = self.cleaned_data.get('cpf', '')
        # O Allauth cuida de salvar o user depois de chamar esse método
        return user


# ── Formulários que você já tinha no projeto ──────────────────

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