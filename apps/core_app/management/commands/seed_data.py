from django.core.management.base import BaseCommand
from apps.catalog.models import Category, Brand, Product, Stock
from apps.plans.models import ServicePlan, PlanFeature
from apps.events.models import Event
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Popula o banco com dados iniciais'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando categorias...')
        categories_data = [
            {'name': 'Rações', 'icon': 'fa-drumstick-bite', 'order': 1},
            {'name': 'Higiene', 'icon': 'fa-soap', 'order': 2},
            {'name': 'Brinquedos', 'icon': 'fa-gamepad', 'order': 3},
            {'name': 'Acessórios', 'icon': 'fa-tag', 'order': 4},
            {'name': 'Remédios', 'icon': 'fa-pills', 'order': 5},
            {'name': 'Pássaros', 'icon': 'fa-feather', 'order': 6},
        ]
        for data in categories_data:
            Category.objects.get_or_create(name=data['name'], defaults=data)

        self.stdout.write('Criando marcas...')
        brands_data = ['PremiumPet', 'VitaPet', 'NaturalLife', 'PetLove', 'ProCão']
        for name in brands_data:
            Brand.objects.get_or_create(name=name)

        self.stdout.write('Criando planos...')
        plans_data = [
            {
                'name': 'Plano Essencial',
                'slug': 'essencial',
                'description': 'O básico com qualidade para o seu pet',
                'price': Decimal('79.90'),
                'food_bags_per_month': 1,
                'grooming_sessions_per_month': 1,
                'color': '#27ae60',
                'order': 1,
                'features': ['Desconto de 5% em produtos', 'Acúmulo de pontos básico'],
            },
            {
                'name': 'Plano Premium',
                'slug': 'premium',
                'description': 'O melhor para o seu companheiro',
                'price': Decimal('149.90'),
                'food_bags_per_month': 2,
                'grooming_sessions_per_month': 2,
                'includes_health_plan': True,
                'is_featured': True,
                'color': '#E85D26',
                'order': 2,
                'features': ['Desconto de 15% em produtos', 'Acúmulo de pontos dobrado', 'Plano de saúde básico'],
            },
            {
                'name': 'Plano Elite',
                'slug': 'elite',
                'description': 'Para quem quer o máximo para seu pet',
                'price': Decimal('249.90'),
                'food_bags_per_month': 4,
                'grooming_sessions_per_month': 4,
                'includes_health_plan': True,
                'color': '#8e44ad',
                'order': 3,
                'features': ['Desconto de 25% em produtos', 'Pontos em dobro + bônus', 'Plano de saúde completo', 'Entrega grátis'],
            },
        ]
        for data in plans_data:
            features = data.pop('features')
            plan, created = ServicePlan.objects.get_or_create(slug=data['slug'], defaults=data)
            if created:
                for feat in features:
                    PlanFeature.objects.create(plan=plan, description=feat)

        self.stdout.write('Criando evento de exemplo...')
        Event.objects.get_or_create(
            slug='feira-adocao-2024',
            defaults={
                'title': 'Feira de Adoção',
                'event_type': 'adoption',
                'description': 'Venha adotar um novo amigo! Temos cães e gatos esperando por um lar amoroso.',
                'short_description': 'Encontre seu novo melhor amigo!',
                'start_date': timezone.now() + timedelta(days=7),
                'location': 'Gateen Petshop — Rua dos Pets, 123',
                'is_featured': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('✅ Dados iniciais criados com sucesso!'))