from django.db import models
from django.utils import timezone
import uuid


class Cart(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'

    def __str__(self):
        return f'Carrinho de {self.user or self.session_key}'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Item do Carrinho'
        unique_together = ('cart', 'product')

    @property
    def subtotal(self):
        return self.product.current_price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('preparing', 'Em preparo'),
        ('ready', 'Pronto para retirada'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregue'),
        ('cancelled', 'Cancelado'),
    ]
    DELIVERY_CHOICES = [
        ('pickup', 'Retirada na loja'),
        ('delivery', 'Entrega em domicílio'),
    ]
    PAYMENT_CHOICES = [
        ('credit_card', 'Cartão de crédito'),
        ('debit_card', 'Cartão de débito'),
        ('pix', 'PIX'),
        ('cash', 'Dinheiro'),
        ('loyalty_points', 'Pontos de fidelidade'),
    ]

    order_number = models.CharField(max_length=20, unique=True, verbose_name='Número do pedido')
    user = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='orders', verbose_name='Cliente')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_CHOICES, verbose_name='Tipo de entrega')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, verbose_name='Forma de pagamento')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Desconto')
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Frete')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total')
    address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Endereço de entrega')
    notes = models.TextField(blank=True, verbose_name='Observações')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.order_number}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f'GT{timezone.now().strftime("%Y%m%d")}{str(uuid.uuid4().int)[:6]}'
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items', verbose_name='Pedido'
    )
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.PROTECT,
        verbose_name='Produto'
    )
    quantity = models.PositiveIntegerField(verbose_name='Quantidade')
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Preço unitário'
    )

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f'{self.quantity}x {self.product}'

    @property
    def subtotal(self):
        # Guarda contra None em linhas vazias do Admin inline
        if self.unit_price is None or self.quantity is None:
            return 0
        return self.unit_price * self.quantity

    def get_subtotal_display(self):
        """Método seguro para exibir no Admin inline."""
        return f'R$ {self.subtotal:.2f}'
    get_subtotal_display.short_description = 'Subtotal'


class CashRegister(models.Model):
    STATUS_CHOICES = [
        ('open', 'Aberto'),
        ('closed', 'Fechado'),
    ]
    TRANSACTION_TYPES = [
        ('sale', 'Venda'),
        ('expense', 'Despesa'),
        ('withdrawal', 'Sangria'),
        ('deposit', 'Suprimento'),
    ]

    opened_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='cash_registers_opened')
    closed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='cash_registers_closed')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Saldo de abertura')
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Saldo de fechamento')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    class Meta:
        verbose_name = 'Caixa'
        verbose_name_plural = 'Caixas'

    def __str__(self):
        return f'Caixa {self.opened_at.strftime("%d/%m/%Y %H:%M")}'


class CashTransaction(models.Model):
    PAYMENT_CHOICES = [
        ('credit_card', 'Cartão de crédito'),
        ('debit_card', 'Cartão de débito'),
        ('pix', 'PIX'),
        ('cash', 'Dinheiro'),
    ]

    cash_register = models.ForeignKey(CashRegister, on_delete=models.PROTECT, related_name='transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(max_length=15, choices=CashRegister.TRANSACTION_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Transação de Caixa'
        verbose_name_plural = 'Transações de Caixa'