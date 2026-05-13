from django.db import models


class ServicePlan(models.Model):
    PERIOD_CHOICES = [
        ('monthly', 'Mensal'),
        ('quarterly', 'Trimestral'),
        ('annual', 'Anual'),
    ]

    name = models.CharField(max_length=100, verbose_name='Nome do Plano')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Descrição')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço')
    period = models.CharField(max_length=15, choices=PERIOD_CHOICES, default='monthly', verbose_name='Período')
    food_bags_per_month = models.PositiveIntegerField(default=0, verbose_name='Sacos de ração/mês')
    grooming_sessions_per_month = models.PositiveIntegerField(default=0, verbose_name='Banhos e tosas/mês')
    includes_health_plan = models.BooleanField(default=False, verbose_name='Inclui plano de saúde')
    health_plan_details = models.TextField(blank=True, verbose_name='Detalhes do plano de saúde')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    is_featured = models.BooleanField(default=False, verbose_name='Destaque')
    color = models.CharField(max_length=7, default='#E85D26', verbose_name='Cor do card')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Plano de Serviço'
        verbose_name_plural = 'Planos de Serviço'
        ordering = ['order', 'price']

    def __str__(self):
        return self.name


class PlanFeature(models.Model):
    plan = models.ForeignKey(ServicePlan, on_delete=models.CASCADE, related_name='features')
    description = models.CharField(max_length=200, verbose_name='Benefício')
    is_included = models.BooleanField(default=True, verbose_name='Incluído')

    class Meta:
        verbose_name = 'Benefício do Plano'
        verbose_name_plural = 'Benefícios do Plano'

    def __str__(self):
        return self.description


class UserPlan(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('cancelled', 'Cancelado'),
        ('expired', 'Expirado'),
        ('pending', 'Pendente'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='plans', verbose_name='Usuário')
    plan = models.ForeignKey(ServicePlan, on_delete=models.PROTECT, verbose_name='Plano')
    pet = models.ForeignKey('accounts.Pet', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Pet')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    start_date = models.DateField(verbose_name='Data de início')
    end_date = models.DateField(verbose_name='Data de término')
    food_bags_used = models.PositiveIntegerField(default=0, verbose_name='Sacos usados no mês')
    grooming_sessions_used = models.PositiveIntegerField(default=0, verbose_name='Banhos usados no mês')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Plano do Usuário'
        verbose_name_plural = 'Planos dos Usuários'

    def __str__(self):
        return f'{self.user.get_full_name()} — {self.plan.name}'

    @property
    def food_bags_remaining(self):
        return self.plan.food_bags_per_month - self.food_bags_used

    @property
    def grooming_sessions_remaining(self):
        return self.plan.grooming_sessions_per_month - self.grooming_sessions_used