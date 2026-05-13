from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name='Descrição')
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='Imagem')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Ícone FontAwesome')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True, verbose_name='Logo')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    SPECIES_CHOICES = [
        ('all', 'Todos'),
        ('dog', 'Cães'),
        ('cat', 'Gatos'),
        ('bird', 'Pássaros'),
        ('fish', 'Peixes'),
        ('other', 'Outros'),
    ]

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='Categoria')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name='Marca')
    name = models.CharField(max_length=200, verbose_name='Nome')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Descrição')
    short_description = models.CharField(max_length=300, blank=True, verbose_name='Descrição curta')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço')
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Preço promocional')
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name='Peso (kg)')
    species = models.CharField(max_length=10, choices=SPECIES_CHOICES, default='all', verbose_name='Espécie')
    image = models.ImageField(upload_to='products/', verbose_name='Imagem principal')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    is_featured = models.BooleanField(default=False, verbose_name='Destaque')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        return self.promotional_price if self.promotional_price else self.price

    @property
    def has_discount(self):
        return bool(self.promotional_price and self.promotional_price < self.price)

    @property
    def discount_percentage(self):
        if self.has_discount:
            return int(((self.price - self.promotional_price) / self.price) * 100)
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Produto')
    image = models.ImageField(upload_to='products/gallery/', verbose_name='Imagem')
    alt = models.CharField(max_length=200, blank=True, verbose_name='Texto alternativo')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Imagem do Produto'
        verbose_name_plural = 'Imagens do Produto'


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Entrada'),
        ('out', 'Saída'),
        ('adjustment', 'Ajuste'),
        ('return', 'Devolução'),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_movements', verbose_name='Produto')
    movement_type = models.CharField(max_length=15, choices=MOVEMENT_TYPES, verbose_name='Tipo')
    quantity = models.IntegerField(verbose_name='Quantidade')
    current_stock = models.IntegerField(verbose_name='Estoque após movimento')
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Custo unitário')
    reason = models.CharField(max_length=300, blank=True, verbose_name='Motivo')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, verbose_name='Registrado por')

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.name} — {self.get_movement_type_display()} ({self.quantity})'


class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='stock', verbose_name='Produto')
    quantity = models.IntegerField(default=0, verbose_name='Quantidade em estoque')
    min_quantity = models.IntegerField(default=5, verbose_name='Quantidade mínima')
    reserved_quantity = models.IntegerField(default=0, verbose_name='Quantidade reservada')

    class Meta:
        verbose_name = 'Estoque'
        verbose_name_plural = 'Estoques'

    def __str__(self):
        return f'Estoque: {self.product.name} ({self.quantity})'

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    @property
    def is_low(self):
        return self.quantity <= self.min_quantity

    @property
    def is_out(self):
        return self.quantity <= 0