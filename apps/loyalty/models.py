from django.db import models


class LoyaltyRule(models.Model):
    RULE_TYPES = [
        ('brand_purchase', 'Compra por marca'),
        ('product_purchase', 'Compra de produto específico'),
        ('amount_spent', 'Valor gasto'),
        ('category_purchase', 'Compra por categoria'),
    ]
    REWARD_TYPES = [
        ('gift_product', 'Produto brinde'),
        ('discount_percent', 'Desconto percentual'),
        ('loyalty_points', 'Pontos de fidelidade'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nome da regra')
    description = models.TextField(verbose_name='Descrição')
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, verbose_name='Tipo de regra')
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES, verbose_name='Tipo de recompensa')
    trigger_brand = models.ForeignKey('catalog.Brand', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Marca gatilho')
    trigger_product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='trigger_rules', verbose_name='Produto gatilho')
    trigger_quantity = models.PositiveIntegerField(default=2, verbose_name='Quantidade necessária')
    trigger_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Valor mínimo')
    reward_product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='reward_rules', verbose_name='Produto brinde')
    reward_discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Percentual de desconto')
    reward_points = models.PositiveIntegerField(default=0, verbose_name='Pontos de recompensa')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    valid_from = models.DateField(null=True, blank=True, verbose_name='Válido de')
    valid_until = models.DateField(null=True, blank=True, verbose_name='Válido até')

    class Meta:
        verbose_name = 'Regra de Fidelidade'
        verbose_name_plural = 'Regras de Fidelidade'

    def __str__(self):
        return self.name


class LoyaltyAccount(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='loyalty_account', verbose_name='Usuário')
    points = models.IntegerField(default=0, verbose_name='Pontos')
    lifetime_points = models.IntegerField(default=0, verbose_name='Pontos acumulados no total')
    level = models.CharField(max_length=20, default='bronze', verbose_name='Nível')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conta Fidelidade'
        verbose_name_plural = 'Contas Fidelidade'

    def __str__(self):
        return f'Fidelidade de {self.user.get_full_name()}'

    def update_level(self):
        if self.lifetime_points >= 5000:
            self.level = 'diamond'
        elif self.lifetime_points >= 2000:
            self.level = 'gold'
        elif self.lifetime_points >= 500:
            self.level = 'silver'
        else:
            self.level = 'bronze'
        self.save()


class LoyaltyTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('earn', 'Ganho'),
        ('redeem', 'Resgate'),
        ('expire', 'Expirado'),
        ('bonus', 'Bônus'),
    ]

    account = models.ForeignKey(LoyaltyAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    points = models.IntegerField()
    description = models.CharField(max_length=300)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Transação de Fidelidade'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.account.user.get_full_name()} — {self.points} pts'