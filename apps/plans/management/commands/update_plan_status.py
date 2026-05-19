from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.plans.models import UserPlan

class Command(BaseCommand):
    help = 'Varre o banco de dados e marca como expirados os planos que passaram da data de término.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando verificação de planos expirados...')
        
        today = timezone.now().date()
        
        # Busca planos ativos cuja data de término é menor que a data de hoje
        expired_plans = UserPlan.objects.filter(
            status='active', 
            end_date__lt=today
        )
        
        count = expired_plans.count()
        
        if count > 0:
            # Faz um update em massa (muito mais rápido do que um loop for)
            expired_plans.update(status='expired')
            self.stdout.write(self.style.SUCCESS(f'✅ {count} plano(s) marcado(s) como expirado(s).'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Nenhum plano ativo encontrava-se expirado.'))