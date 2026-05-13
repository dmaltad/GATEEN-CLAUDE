from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Cria os grupos de funcionários com permissões corretas'

    def handle(self, *args, **kwargs):
        self.stdout.write('🔑 Configurando grupos de acesso...')

        # ── DEFINIÇÃO DE PERMISSÕES POR GRUPO ──────────────────────────
        groups_config = {

            'Gerente': {
                'description': 'Acesso total ao sistema',
                'permissions': [
                    # Usuários
                    ('accounts', 'user', ['view', 'add', 'change', 'delete']),
                    ('accounts', 'address', ['view', 'add', 'change', 'delete']),
                    ('accounts', 'pet', ['view', 'add', 'change', 'delete']),
                    # Catálogo
                    ('catalog', 'product', ['view', 'add', 'change', 'delete']),
                    ('catalog', 'category', ['view', 'add', 'change', 'delete']),
                    ('catalog', 'brand', ['view', 'add', 'change', 'delete']),
                    ('catalog', 'stock', ['view', 'add', 'change', 'delete']),
                    ('catalog', 'stockmovement', ['view', 'add', 'change', 'delete']),
                    # Pedidos
                    ('orders', 'order', ['view', 'add', 'change', 'delete']),
                    ('orders', 'orderitem', ['view', 'add', 'change', 'delete']),
                    ('orders', 'cashregister', ['view', 'add', 'change', 'delete']),
                    ('orders', 'cashtransaction', ['view', 'add', 'change', 'delete']),
                    # Planos
                    ('plans', 'serviceplan', ['view', 'add', 'change', 'delete']),
                    ('plans', 'userplan', ['view', 'add', 'change', 'delete']),
                    ('plans', 'planfeature', ['view', 'add', 'change', 'delete']),
                    # Fidelidade
                    ('loyalty', 'loyaltyrule', ['view', 'add', 'change', 'delete']),
                    ('loyalty', 'loyaltyaccount', ['view', 'add', 'change', 'delete']),
                    ('loyalty', 'loyaltytransaction', ['view', 'add', 'change', 'delete']),
                    # Eventos
                    ('events', 'event', ['view', 'add', 'change', 'delete']),
                    ('events', 'promotion', ['view', 'add', 'change', 'delete']),
                    # Auth
                    ('auth', 'group', ['view', 'add', 'change', 'delete']),
                ],
            },

            'Estoquista': {
                'description': 'Gerencia produtos e estoque',
                'permissions': [
                    ('catalog', 'product', ['view', 'add', 'change']),
                    ('catalog', 'category', ['view']),
                    ('catalog', 'brand', ['view']),
                    ('catalog', 'stock', ['view', 'change']),
                    ('catalog', 'stockmovement', ['view', 'add']),
                    ('orders', 'order', ['view']),
                    ('orders', 'orderitem', ['view']),
                ],
            },

            'Atendimento': {
                'description': 'Gerencia pedidos e clientes',
                'permissions': [
                    ('accounts', 'user', ['view']),
                    ('accounts', 'address', ['view']),
                    ('accounts', 'pet', ['view']),
                    ('catalog', 'product', ['view']),
                    ('catalog', 'stock', ['view']),
                    ('orders', 'order', ['view', 'change']),
                    ('orders', 'orderitem', ['view']),
                    ('orders', 'cashregister', ['view', 'add', 'change']),
                    ('orders', 'cashtransaction', ['view', 'add']),
                    ('plans', 'userplan', ['view', 'change']),
                    ('loyalty', 'loyaltyaccount', ['view', 'change']),
                    ('loyalty', 'loyaltytransaction', ['view', 'add']),
                ],
            },

            'Marketing': {
                'description': 'Gerencia eventos e promoções',
                'permissions': [
                    ('events', 'event', ['view', 'add', 'change', 'delete']),
                    ('events', 'promotion', ['view', 'add', 'change', 'delete']),
                    ('catalog', 'product', ['view']),
                    ('catalog', 'category', ['view']),
                    ('catalog', 'brand', ['view']),
                    ('loyalty', 'loyaltyrule', ['view', 'add', 'change']),
                ],
            },
        }

        for group_name, config in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)
            group.permissions.clear()

            for app_label, model_name, actions in config['permissions']:
                try:
                    ct = ContentType.objects.get(
                        app_label=app_label,
                        model=model_name,
                    )
                    for action in actions:
                        codename = f'{action}_{model_name}'
                        try:
                            perm = Permission.objects.get(
                                codename=codename,
                                content_type=ct,
                            )
                            group.permissions.add(perm)
                        except Permission.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  ⚠ Permissão não encontrada: {codename}'
                                )
                            )
                except ContentType.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ ContentType não encontrado: {app_label}.{model_name}'
                        )
                    )

            status = '✅ Criado' if created else '🔄 Atualizado'
            self.stdout.write(f'  {status}: {group_name}')

        self.stdout.write(self.style.SUCCESS('\n🎉 Grupos configurados com sucesso!'))
        self.stdout.write(
            '\nGrupos disponíveis:\n'
            '  • Gerente     — acesso total\n'
            '  • Estoquista  — produtos e estoque\n'
            '  • Atendimento — pedidos e clientes\n'
            '  • Marketing   — eventos e promoções\n'
        )