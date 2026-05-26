from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
from apps.events.models import Event


class Command(BaseCommand):
    help = 'Popula o banco com eventos de exemplo para a Gateen Petshop'

    def handle(self, *args, **kwargs):
        self.stdout.write('📅 Criando eventos...')

        now = timezone.now()

        events_data = [
            # ── Eventos futuros ──────────────────────────────────────
            {
                'title': 'Feira de Adoção — Junho 2026',
                'event_type': 'adoption',
                'short_description': 'Encontre seu novo melhor amigo! Cães e gatos esperando por um lar.',
                'description': (
                    'A Gateen Petshop em parceria com o Canil Municipal realiza mais uma '
                    'edição da Feira de Adoção. Venha conhecer nossos animais resgatados, '
                    'todos vacinados e vermifugados. Traga a família e abra seu coração!'
                ),
                'start_date': now + timedelta(days=7),
                'end_date':   now + timedelta(days=7, hours=6),
                'location': 'Gateen Petshop — Rua dos Pets, 123, Centro',
                'is_online': False,
                'is_active': True,
                'is_featured': True,
            },
            {
                'title': 'Workshop de Adestramento Básico',
                'event_type': 'workshop',
                'short_description': 'Aprenda técnicas de adestramento positivo com especialistas.',
                'description': (
                    'Nosso adestrador certificado Marcos Oliveira vai ensinar os fundamentos '
                    'do adestramento com reforço positivo. O workshop é presencial, para até '
                    '15 tutores com seus pets. Inclui material didático e certificado de participação.'
                ),
                'start_date': now + timedelta(days=14),
                'end_date':   now + timedelta(days=14, hours=3),
                'location': 'Gateen Petshop — Sala de Eventos, 2º andar',
                'is_online': False,
                'is_active': True,
                'is_featured': True,
            },
            {
                'title': 'Dia de Spa para Pets',
                'event_type': 'store',
                'short_description': 'Banho, tosa e hidratação com 30% de desconto por um dia.',
                'description': (
                    'Um dia especial dedicado ao bem-estar do seu pet! Oferecemos pacote completo '
                    'de banho, tosa higiênica, hidratação de pelagem e corte de unhas com 30% de '
                    'desconto. Vagas limitadas — faça sua reserva antecipada.'
                ),
                'start_date': now + timedelta(days=21),
                'end_date':   now + timedelta(days=21, hours=8),
                'location': 'Gateen Petshop — Setor de Banho e Tosa',
                'is_online': False,
                'is_active': True,
                'is_featured': False,
            },
            {
                'title': 'Live: Nutrição Felina com Dr. Ricardo Nunes',
                'event_type': 'workshop',
                'short_description': 'Tire suas dúvidas sobre alimentação saudável para gatos.',
                'description': (
                    'O médico veterinário Dr. Ricardo Nunes, especialista em nutrição animal, '
                    'vai responder perguntas ao vivo sobre dieta, suplementação e alimentação '
                    'natural para gatos. Evento gratuito e aberto ao público.'
                ),
                'start_date': now + timedelta(days=10),
                'end_date':   now + timedelta(days=10, hours=2),
                'location': '',
                'is_online': True,
                'online_link': 'https://youtube.com/gateenpetshop',
                'is_active': True,
                'is_featured': False,
            },
            {
                'title': 'Promoção Dia dos Namorados — Presentes para Pets',
                'event_type': 'promotion',
                'short_description': 'Presentes especiais para o amor de 4 patas com até 25% off.',
                'description': (
                    'No Dia dos Namorados, que tal presentear também seu pet? Selecionamos '
                    'os produtos mais amados — brinquedos, petiscos gourmet, camas e muito mais — '
                    'com descontos de até 25%. A promoção vale para compras na loja física e online.'
                ),
                'start_date': now + timedelta(days=18),
                'end_date':   now + timedelta(days=19),
                'location': 'Gateen Petshop — Loja física e site',
                'is_online': False,
                'is_active': True,
                'is_featured': True,
            },
            {
                'title': 'Campanha de Vacinação Antirrábica',
                'event_type': 'store',
                'short_description': 'Vacinação gratuita em parceria com a Prefeitura Municipal.',
                'description': (
                    'Em parceria com a Secretaria Municipal de Saúde, realizaremos um ponto '
                    'de vacinação antirrábica gratuita para cães e gatos. Traga o cartão de '
                    'vacinação do seu pet e um documento de identificação do tutor.'
                ),
                'start_date': now + timedelta(days=30),
                'end_date':   now + timedelta(days=30, hours=5),
                'location': 'Estacionamento da Gateen Petshop',
                'is_online': False,
                'is_active': True,
                'is_featured': True,
            },
            {
                'title': 'Workshop de Primeiros Socorros para Pets',
                'event_type': 'workshop',
                'short_description': 'Aprenda o que fazer em emergências com seu animal.',
                'description': (
                    'A médica veterinária Dra. Ana Paula ensina as principais técnicas de '
                    'primeiros socorros para cães e gatos: RCP, manobra de Heimlich, controle '
                    'de hemorragias e como agir em casos de envenenamento. Vagas limitadas.'
                ),
                'start_date': now + timedelta(days=45),
                'end_date':   now + timedelta(days=45, hours=4),
                'location': 'Gateen Petshop — Sala de Eventos',
                'is_online': False,
                'is_active': True,
                'is_featured': False,
            },
            {
                'title': 'Concurso de Fantasias Pet — Halloween',
                'event_type': 'store',
                'short_description': 'Vista seu pet e concorra a prêmios incríveis!',
                'description': (
                    'Chegou a edição mais assustadora do ano! Traga seu pet fantasiado e '
                    'concorra a prêmios em três categorias: Mais Assustador, Mais Criativo '
                    'e Mais Fofo. O evento terá fotógrafo profissional, petiscos temáticos '
                    'e sorteios para todos os participantes.'
                ),
                'start_date': now + timedelta(days=60),
                'end_date':   now + timedelta(days=60, hours=4),
                'location': 'Gateen Petshop — Área externa',
                'is_online': False,
                'is_active': True,
                'is_featured': False,
            },
        ]

        created = 0
        skipped = 0

        for data in events_data:
            online_link = data.pop('online_link', '')
            slug = slugify(data['title'])

            # Garante slug único
            base_slug = slug
            counter = 1
            while Event.objects.filter(slug=slug).exclude(title=data['title']).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            # Tenta usar uma imagem placeholder (não obrigatória)
            event, was_created = Event.objects.get_or_create(
                slug=slug,
                defaults={
                    **data,
                    'online_link': online_link,
                    'image': '',  # sem imagem por padrão
                }
            )

            if was_created:
                created += 1
                self.stdout.write(f'  ✅ Criado: {event.title}')
            else:
                skipped += 1
                self.stdout.write(f'  ⏭  Já existe: {event.title}')

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Concluído! {created} evento(s) criado(s), {skipped} já existia(m).'
        ))