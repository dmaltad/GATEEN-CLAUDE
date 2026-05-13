from django.db import models
from django.utils import timezone


class Event(models.Model):
    EVENT_TYPES = [
        ('store', 'Evento na loja'),
        ('external', 'Evento externo'),
        ('promotion', 'Promoção'),
        ('workshop', 'Workshop'),
        ('adoption', 'Feira de adoção'),
    ]

    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(unique=True)
    event_type = models.CharField(max_length=15, choices=EVENT_TYPES, verbose_name='Tipo')
    description = models.TextField(verbose_name='Descrição')
    short_description = models.CharField(max_length=300, verbose_name='Descrição curta')
    image = models.ImageField(upload_to='events/', verbose_name='Imagem')
    banner = models.ImageField(upload_to='events/banners/', null=True, blank=True, verbose_name='Banner')
    start_date = models.DateTimeField(verbose_name='Data de início')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Data de término')
    location = models.CharField(max_length=300, blank=True, verbose_name='Local')
    is_online = models.BooleanField(default=False, verbose_name='Online')
    online_link = models.URLField(blank=True, verbose_name='Link online')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    is_featured = models.BooleanField(default=False, verbose_name='Destaque')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['start_date']

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    @property
    def is_ongoing(self):
        if self.end_date:
            return self.start_date <= timezone.now() <= self.end_date
        return False


class Promotion(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentual'),
        ('fixed', 'Valor fixo'),
        ('free_shipping', 'Frete grátis'),
    ]

    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Descrição')
    image = models.ImageField(upload_to='promotions/', null=True, blank=True, verbose_name='Imagem')
    banner = models.ImageField(upload_to='promotions/banners/', null=True, blank=True, verbose_name='Banner')
    discount_type = models.CharField(max_length=15, choices=DISCOUNT_TYPES, verbose_name='Tipo de desconto')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor do desconto')
    coupon_code = models.CharField(max_length=20, blank=True, unique=True, verbose_name='Código do cupom')
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Compra mínima')
    max_uses = models.PositiveIntegerField(null=True, blank=True, verbose_name='Limite de usos')
    used_count = models.PositiveIntegerField(default=0, verbose_name='Vezes utilizado')
    applicable_products = models.ManyToManyField('catalog.Product', blank=True, verbose_name='Produtos')
    applicable_categories = models.ManyToManyField('catalog.Category', blank=True, verbose_name='Categorias')
    start_date = models.DateTimeField(verbose_name='Início')
    end_date = models.DateTimeField(verbose_name='Término')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Promoção'
        verbose_name_plural = 'Promoções'

    def __str__(self):
        return self.title

    @property
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date