from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='E-mail')
    first_name = models.CharField(max_length=100, verbose_name='Nome')
    last_name = models.CharField(max_length=100, verbose_name='Sobrenome')
    cpf = models.CharField(max_length=14, blank=True, verbose_name='CPF')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Foto')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='Usuário')
    label = models.CharField(max_length=50, default='Casa', verbose_name='Identificação')
    cep = models.CharField(max_length=9, verbose_name='CEP')
    street = models.CharField(max_length=200, verbose_name='Rua')
    number = models.CharField(max_length=10, verbose_name='Número')
    complement = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=100, verbose_name='Bairro')
    city = models.CharField(max_length=100, verbose_name='Cidade')
    state = models.CharField(max_length=2, verbose_name='Estado')
    is_default = models.BooleanField(default=False, verbose_name='Endereço padrão')

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f'{self.label} - {self.street}, {self.number}'


class Pet(models.Model):
    SPECIES_CHOICES = [
        ('dog', 'Cachorro'),
        ('cat', 'Gato'),
        ('bird', 'Pássaro'),
        ('fish', 'Peixe'),
        ('other', 'Outro'),
    ]
    SIZE_CHOICES = [
        ('small', 'Pequeno'),
        ('medium', 'Médio'),
        ('large', 'Grande'),
        ('giant', 'Gigante'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets', verbose_name='Dono')
    name = models.CharField(max_length=100, verbose_name='Nome')
    species = models.CharField(max_length=10, choices=SPECIES_CHOICES, verbose_name='Espécie')
    breed = models.CharField(max_length=100, blank=True, verbose_name='Raça')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, verbose_name='Porte')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    photo = models.ImageField(upload_to='pets/', null=True, blank=True, verbose_name='Foto')
    observations = models.TextField(blank=True, verbose_name='Observações')

    class Meta:
        verbose_name = 'Pet'
        verbose_name_plural = 'Pets'

    def __str__(self):
        return f'{self.name} ({self.owner.get_full_name()})'