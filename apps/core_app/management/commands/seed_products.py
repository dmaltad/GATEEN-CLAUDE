from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Category, Brand, Product, Stock
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Popula o banco com produtos de exemplo para a Gateen Petshop'

    def handle(self, *args, **kwargs):
        self.stdout.write('🐾 Iniciando população de produtos...')

        # Garante que categorias e marcas existam
        categories = {
            'racoes':      self._get_or_create_category('Rações',      'fa-drumstick-bite', 1),
            'higiene':     self._get_or_create_category('Higiene',      'fa-soap',           2),
            'brinquedos':  self._get_or_create_category('Brinquedos',  'fa-gamepad',        3),
            'acessorios':  self._get_or_create_category('Acessórios',  'fa-tag',            4),
            'remedios':    self._get_or_create_category('Remédios',    'fa-pills',          5),
            'passaros':    self._get_or_create_category('Pássaros',    'fa-feather',        6),
            'peixes':      self._get_or_create_category('Peixes',      'fa-fish',           7),
        }

        brands = {
            'premiumpet':   self._get_or_create_brand('PremiumPet'),
            'vitapet':      self._get_or_create_brand('VitaPet'),
            'naturallife':  self._get_or_create_brand('NaturalLife'),
            'petlove':      self._get_or_create_brand('PetLove'),
            'procao':       self._get_or_create_brand('ProCão'),
            'royal':        self._get_or_create_brand('Royal Canin'),
            'pedigree':     self._get_or_create_brand('Pedigree'),
            'whiskas':      self._get_or_create_brand('Whiskas'),
            'golden':       self._get_or_create_brand('Golden'),
            'biofresh':     self._get_or_create_brand('Biofresh'),
        }

        products_data = [

            # ── RAÇÕES PARA CÃES ──────────────────────────────────────────
            {
                'name': 'Ração Royal Canin Medium Adult 15kg',
                'category': categories['racoes'],
                'brand': brands['royal'],
                'price': Decimal('289.90'),
                'promotional_price': Decimal('249.90'),
                'weight': Decimal('15.000'),
                'species': 'dog',
                'description': 'Ração completa para cães adultos de porte médio. Fórmula balanceada com vitaminas e minerais essenciais para a saúde do seu cão.',
                'short_description': 'Ração premium para cães adultos de médio porte, 15kg.',
                'is_featured': True,
            },
            {
                'name': 'Ração Pedigree Adulto Carne 10,1kg',
                'category': categories['racoes'],
                'brand': brands['pedigree'],
                'price': Decimal('129.90'),
                'promotional_price': None,
                'weight': Decimal('10.100'),
                'species': 'dog',
                'description': 'Ração Pedigree para cães adultos sabor carne. Contém antioxidantes naturais e proteínas de alta qualidade.',
                'short_description': 'Ração sabor carne para cães adultos, 10,1kg.',
                'is_featured': True,
            },
            {
                'name': 'Ração Golden Adulto Frango e Arroz 15kg',
                'category': categories['racoes'],
                'brand': brands['golden'],
                'price': Decimal('189.90'),
                'promotional_price': Decimal('169.90'),
                'weight': Decimal('15.000'),
                'species': 'dog',
                'description': 'Ração Golden para cães adultos, sabor frango e arroz. Excelente palatabilidade e digestibilidade.',
                'short_description': 'Ração frango e arroz para cães adultos, 15kg.',
                'is_featured': False,
            },
            {
                'name': 'Ração ProCão Filhote Todas as Raças 20kg',
                'category': categories['racoes'],
                'brand': brands['procao'],
                'price': Decimal('159.90'),
                'promotional_price': None,
                'weight': Decimal('20.000'),
                'species': 'dog',
                'description': 'Ração completa para filhotes de todas as raças. Rica em DHA para o desenvolvimento cerebral e ósseo.',
                'short_description': 'Ração para filhotes de todas as raças, 20kg.',
                'is_featured': False,
            },
            {
                'name': 'Ração PremiumPet Senior Cães Idosos 10kg',
                'category': categories['racoes'],
                'brand': brands['premiumpet'],
                'price': Decimal('219.90'),
                'promotional_price': Decimal('199.90'),
                'weight': Decimal('10.000'),
                'species': 'dog',
                'description': 'Formulada especialmente para cães acima de 7 anos. Baixo teor de fósforo e sódio para proteção renal e cardíaca.',
                'short_description': 'Ração especial para cães idosos, 10kg.',
                'is_featured': True,
            },
            {
                'name': 'Ração NaturalLife Grain Free Cão Adulto 12kg',
                'category': categories['racoes'],
                'brand': brands['naturallife'],
                'price': Decimal('259.90'),
                'promotional_price': None,
                'weight': Decimal('12.000'),
                'species': 'dog',
                'description': 'Ração sem grãos para cães com sensibilidade alimentar. Proteína de frango desidratado como primeiro ingrediente.',
                'short_description': 'Ração sem grãos para cães sensíveis, 12kg.',
                'is_featured': False,
            },

            # ── RAÇÕES PARA GATOS ─────────────────────────────────────────
            {
                'name': 'Ração Royal Canin Indoor Cat 4kg',
                'category': categories['racoes'],
                'brand': brands['royal'],
                'price': Decimal('139.90'),
                'promotional_price': Decimal('119.90'),
                'weight': Decimal('4.000'),
                'species': 'cat',
                'description': 'Ração para gatos que vivem em ambientes fechados. Controla odores e reduz a formação de bolas de pelo.',
                'short_description': 'Ração para gatos de interior, 4kg.',
                'is_featured': True,
            },
            {
                'name': 'Ração Whiskas Adulto Frango 10,1kg',
                'category': categories['racoes'],
                'brand': brands['whiskas'],
                'price': Decimal('109.90'),
                'promotional_price': None,
                'weight': Decimal('10.100'),
                'species': 'cat',
                'description': 'Ração Whiskas com sabor frango para gatos adultos. Contém taurina para saúde ocular e cardíaca.',
                'short_description': 'Ração sabor frango para gatos adultos, 10,1kg.',
                'is_featured': False,
            },
            {
                'name': 'Ração Biofresh Gato Castrado 7,5kg',
                'category': categories['racoes'],
                'brand': brands['biofresh'],
                'price': Decimal('179.90'),
                'promotional_price': Decimal('159.90'),
                'weight': Decimal('7.500'),
                'species': 'cat',
                'description': 'Ração especial para gatos castrados. Controle de peso e prevenção de problemas urinários.',
                'short_description': 'Ração para gatos castrados, controle de peso, 7,5kg.',
                'is_featured': False,
            },
            {
                'name': 'Ração VitaPet Filhote Gato 3kg',
                'category': categories['racoes'],
                'brand': brands['vitapet'],
                'price': Decimal('89.90'),
                'promotional_price': None,
                'weight': Decimal('3.000'),
                'species': 'cat',
                'description': 'Formulada para filhotes de gato de até 12 meses. Alta densidade energética para o crescimento saudável.',
                'short_description': 'Ração para filhotes de gato, 3kg.',
                'is_featured': False,
            },

            # ── HIGIENE ───────────────────────────────────────────────────
            {
                'name': 'Shampoo PetLove Pelos Claros 500ml',
                'category': categories['higiene'],
                'brand': brands['petlove'],
                'price': Decimal('34.90'),
                'promotional_price': Decimal('28.90'),
                'weight': Decimal('0.500'),
                'species': 'dog',
                'description': 'Shampoo especial para cães com pelagem clara. Realça o brilho e a cor natural sem ressecar.',
                'short_description': 'Shampoo para pelos claros, 500ml.',
                'is_featured': True,
            },
            {
                'name': 'Shampoo NaturalLife Antipulgas 400ml',
                'category': categories['higiene'],
                'brand': brands['naturallife'],
                'price': Decimal('42.90'),
                'promotional_price': None,
                'weight': Decimal('0.400'),
                'species': 'all',
                'description': 'Shampoo com princípios ativos que repelem pulgas e carrapatos. Fórmula suave com extrato de citronela.',
                'short_description': 'Shampoo antipulgas natural, 400ml.',
                'is_featured': False,
            },
            {
                'name': 'Condicionador PremiumPet Pelos Longos 300ml',
                'category': categories['higiene'],
                'brand': brands['premiumpet'],
                'price': Decimal('38.90'),
                'promotional_price': None,
                'weight': Decimal('0.300'),
                'species': 'all',
                'description': 'Condicionador desembaraçante para cães e gatos de pelos longos. Facilita a escovação e reduz a estática.',
                'short_description': 'Condicionador desembaraçante para pelos longos, 300ml.',
                'is_featured': False,
            },
            {
                'name': 'Escova de Dentes Kit Cão e Gato',
                'category': categories['higiene'],
                'brand': brands['petlove'],
                'price': Decimal('22.90'),
                'promotional_price': Decimal('18.90'),
                'weight': Decimal('0.100'),
                'species': 'all',
                'description': 'Kit completo com escova e pasta de dente sabor frango. Previne tártaro e mau hálito.',
                'short_description': 'Kit escova + pasta dental sabor frango.',
                'is_featured': False,
            },
            {
                'name': 'Toalha Microfibra Pet Secagem Rápida',
                'category': categories['higiene'],
                'brand': brands['vitapet'],
                'price': Decimal('29.90'),
                'promotional_price': None,
                'weight': Decimal('0.200'),
                'species': 'all',
                'description': 'Toalha de microfibra ultra absorvente para banho de pets. Seca 5x mais rápido que toalhas comuns.',
                'short_description': 'Toalha microfibra de secagem rápida para pets.',
                'is_featured': False,
            },
            {
                'name': 'Perfume Pet Lavanda 100ml',
                'category': categories['higiene'],
                'brand': brands['premiumpet'],
                'price': Decimal('26.90'),
                'promotional_price': Decimal('22.90'),
                'weight': Decimal('0.100'),
                'species': 'all',
                'description': 'Perfume suave de lavanda para pets, sem álcool. Mantém o pet cheiroso entre os banhos.',
                'short_description': 'Colônia de lavanda sem álcool para pets, 100ml.',
                'is_featured': False,
            },

            # ── BRINQUEDOS ────────────────────────────────────────────────
            {
                'name': 'Bola Interativa Kong Classic Vermelho M',
                'category': categories['brinquedos'],
                'brand': brands['petlove'],
                'price': Decimal('59.90'),
                'promotional_price': Decimal('49.90'),
                'weight': Decimal('0.150'),
                'species': 'dog',
                'description': 'Brinquedo interativo de borracha resistente. Pode ser preenchido com petisco para estimular o instinto natural do cão.',
                'short_description': 'Brinquedo interativo de borracha, tamanho M.',
                'is_featured': True,
            },
            {
                'name': 'Arranhador Gato Torre com Corda Sisal',
                'category': categories['brinquedos'],
                'brand': brands['vitapet'],
                'price': Decimal('89.90'),
                'promotional_price': None,
                'weight': Decimal('1.500'),
                'species': 'cat',
                'description': 'Torre arranhador em corda sisal com plataforma. Satisfaz o instinto de arranhar e oferece área de descanso.',
                'short_description': 'Torre arranhador com corda sisal para gatos.',
                'is_featured': True,
            },
            {
                'name': 'Varinha com Pena para Gatos',
                'category': categories['brinquedos'],
                'brand': brands['petlove'],
                'price': Decimal('18.90'),
                'promotional_price': None,
                'weight': Decimal('0.050'),
                'species': 'cat',
                'description': 'Varinha interativa com penas coloridas. Estimula o instinto de caça e promove exercício físico.',
                'short_description': 'Varinha com penas coloridas para gatos.',
                'is_featured': False,
            },
            {
                'name': 'Osso Borracha Natural Cão Grande',
                'category': categories['brinquedos'],
                'brand': brands['naturallife'],
                'price': Decimal('32.90'),
                'promotional_price': Decimal('26.90'),
                'weight': Decimal('0.200'),
                'species': 'dog',
                'description': 'Osso de borracha natural para cães de grande porte. Ajuda na limpeza dos dentes e entretém por horas.',
                'short_description': 'Osso de borracha para cães grandes.',
                'is_featured': False,
            },
            {
                'name': 'Bolinha de Tênis Pet Pack 3un',
                'category': categories['brinquedos'],
                'brand': brands['petlove'],
                'price': Decimal('24.90'),
                'promotional_price': None,
                'weight': Decimal('0.180'),
                'species': 'dog',
                'description': 'Pack com 3 bolinhas de tênis coloridas no tamanho ideal para cães. Ótimas para brincadeiras de busca.',
                'short_description': 'Pack com 3 bolinhas de tênis coloridas.',
                'is_featured': False,
            },

            # ── ACESSÓRIOS ────────────────────────────────────────────────
            {
                'name': 'Coleira Ajustável Nylon Cão M Rosa',
                'category': categories['acessorios'],
                'brand': brands['petlove'],
                'price': Decimal('29.90'),
                'promotional_price': Decimal('24.90'),
                'weight': Decimal('0.080'),
                'species': 'dog',
                'description': 'Coleira em nylon resistente, ajustável, com fivela de segurança. Tamanho M, cor rosa.',
                'short_description': 'Coleira ajustável de nylon tamanho M, rosa.',
                'is_featured': False,
            },
            {
                'name': 'Guia Retrátil 5m até 25kg',
                'category': categories['acessorios'],
                'brand': brands['premiumpet'],
                'price': Decimal('79.90'),
                'promotional_price': Decimal('64.90'),
                'weight': Decimal('0.300'),
                'species': 'dog',
                'description': 'Guia retrátil com trava de segurança para cães até 25kg. Cabo de nylon de 5 metros.',
                'short_description': 'Guia retrátil 5m para cães até 25kg.',
                'is_featured': True,
            },
            {
                'name': 'Cama Pet Pelúcia Redonda P',
                'category': categories['acessorios'],
                'brand': brands['vitapet'],
                'price': Decimal('69.90'),
                'promotional_price': None,
                'weight': Decimal('0.600'),
                'species': 'all',
                'description': 'Cama redonda de pelúcia super macia. Ideal para cães e gatos de pequeno porte. Lavável na máquina.',
                'short_description': 'Cama redonda de pelúcia tamanho P.',
                'is_featured': False,
            },
            {
                'name': 'Caixa Transporte Plástica Nº 3',
                'category': categories['acessorios'],
                'brand': brands['petlove'],
                'price': Decimal('149.90'),
                'promotional_price': Decimal('129.90'),
                'weight': Decimal('2.500'),
                'species': 'all',
                'description': 'Caixa de transporte em plástico resistente número 3, para animais até 12kg. Porta com trava de segurança.',
                'short_description': 'Caixa de transporte Nº3, até 12kg.',
                'is_featured': False,
            },
            {
                'name': 'Bebedouro Automático Inox 500ml',
                'category': categories['acessorios'],
                'brand': brands['premiumpet'],
                'price': Decimal('54.90'),
                'promotional_price': Decimal('44.90'),
                'weight': Decimal('0.400'),
                'species': 'all',
                'description': 'Bebedouro automático com reservatório de inox. Mantém a água sempre fresca e filtrada.',
                'short_description': 'Bebedouro automático de inox, 500ml.',
                'is_featured': True,
            },
            {
                'name': 'Comedouro Elevado Inox Duplo M',
                'category': categories['acessorios'],
                'brand': brands['naturallife'],
                'price': Decimal('89.90'),
                'promotional_price': None,
                'weight': Decimal('0.800'),
                'species': 'dog',
                'description': 'Comedouro elevado com dois potes de inox para água e ração. Reduz o esforço cervical durante a alimentação.',
                'short_description': 'Comedouro elevado inox duplo tamanho M.',
                'is_featured': False,
            },
            {
                'name': 'Mochila Transporte Pet até 8kg Azul',
                'category': categories['acessorios'],
                'brand': brands['petlove'],
                'price': Decimal('199.90'),
                'promotional_price': Decimal('169.90'),
                'weight': Decimal('0.700'),
                'species': 'all',
                'description': 'Mochila para transporte de pets até 8kg. Janela com tela de ventilação e abertura superior e frontal.',
                'short_description': 'Mochila para transporte de pets até 8kg, azul.',
                'is_featured': True,
            },

            # ── REMÉDIOS / SAÚDE ──────────────────────────────────────────
            {
                'name': 'Antipulgas Frontline Plus Cão 10-20kg',
                'category': categories['remedios'],
                'brand': brands['vitapet'],
                'price': Decimal('89.90'),
                'promotional_price': None,
                'weight': Decimal('0.010'),
                'species': 'dog',
                'description': 'Antipulgas e carrapaticida em pipeta. Proteção por até 3 meses. Para cães entre 10 e 20kg.',
                'short_description': 'Antipulgas e carrapaticida pipeta, cães 10–20kg.',
                'is_featured': False,
            },
            {
                'name': 'Suplemento Articular Condroitina + Glucosamina 60 cáps',
                'category': categories['remedios'],
                'brand': brands['premiumpet'],
                'price': Decimal('74.90'),
                'promotional_price': Decimal('64.90'),
                'weight': Decimal('0.120'),
                'species': 'all',
                'description': 'Suplemento para saúde articular de cães e gatos. Auxilia na mobilidade e reduz dores em animais idosos.',
                'short_description': 'Suplemento articular condroitina + glucosamina, 60 cáps.',
                'is_featured': False,
            },
            {
                'name': 'Vermífugo Drontal Cão até 10kg 4 Comp',
                'category': categories['remedios'],
                'brand': brands['vitapet'],
                'price': Decimal('49.90'),
                'promotional_price': None,
                'weight': Decimal('0.020'),
                'species': 'dog',
                'description': 'Vermífugo de amplo espectro para cães até 10kg. Age contra lombrigas, ancilóstomos e outros parasitas intestinais.',
                'short_description': 'Vermífugo para cães até 10kg, 4 comprimidos.',
                'is_featured': False,
            },
            {
                'name': 'Vitamina E + Ômega 3 Pet 60 Cáps',
                'category': categories['remedios'],
                'brand': brands['naturallife'],
                'price': Decimal('59.90'),
                'promotional_price': Decimal('49.90'),
                'weight': Decimal('0.100'),
                'species': 'all',
                'description': 'Suplemento de vitamina E e ômega 3 para pelagem brilhante e saúde cardiovascular de cães e gatos.',
                'short_description': 'Vitamina E + Ômega 3 para pets, 60 cápsulas.',
                'is_featured': False,
            },

            # ── PÁSSAROS ──────────────────────────────────────────────────
            {
                'name': 'Ração Pássaros Tropicais Mistura Premium 500g',
                'category': categories['passaros'],
                'brand': brands['vitapet'],
                'price': Decimal('19.90'),
                'promotional_price': None,
                'weight': Decimal('0.500'),
                'species': 'bird',
                'description': 'Mistura premium de sementes para pássaros tropicais. Contém painço, alpiste, girassol e frutas desidratadas.',
                'short_description': 'Mistura de sementes para pássaros tropicais, 500g.',
                'is_featured': False,
            },
            {
                'name': 'Gaiola Arara Modelo Vitoriana 60cm',
                'category': categories['passaros'],
                'brand': brands['petlove'],
                'price': Decimal('329.90'),
                'promotional_price': Decimal('289.90'),
                'weight': Decimal('4.000'),
                'species': 'bird',
                'description': 'Gaiola modelo vitoriano em metal pintado. Tira-caca removível e porta dupla. Acompanha poleiro e comedouros.',
                'short_description': 'Gaiola vitoriana 60cm com acessórios.',
                'is_featured': False,
            },
            {
                'name': 'Balanço de Madeira para Pássaros',
                'category': categories['passaros'],
                'brand': brands['naturallife'],
                'price': Decimal('14.90'),
                'promotional_price': None,
                'weight': Decimal('0.080'),
                'species': 'bird',
                'description': 'Balanço em madeira natural para enriquecimento ambiental de pássaros. Fácil instalação na gaiola.',
                'short_description': 'Balanço de madeira natural para pássaros.',
                'is_featured': False,
            },

            # ── PEIXES ────────────────────────────────────────────────────
            {
                'name': 'Ração Tetra Goldfish Flocos 52g',
                'category': categories['peixes'],
                'brand': brands['vitapet'],
                'price': Decimal('24.90'),
                'promotional_price': None,
                'weight': Decimal('0.052'),
                'species': 'fish',
                'description': 'Ração em flocos para peixes dourados. Fórmula enriquecida com vitaminas para cores vibrantes e saúde.',
                'short_description': 'Ração em flocos para peixes dourados, 52g.',
                'is_featured': False,
            },
            {
                'name': 'Aquário Kit Completo 30 Litros',
                'category': categories['peixes'],
                'brand': brands['petlove'],
                'price': Decimal('249.90'),
                'promotional_price': Decimal('219.90'),
                'weight': Decimal('5.000'),
                'species': 'fish',
                'description': 'Kit completo com aquário 30L, filtro interno, termômetro, pedras decorativas e manual de manutenção.',
                'short_description': 'Kit aquário 30 litros com filtro e acessórios.',
                'is_featured': False,
            },
            {
                'name': 'Condicionador de Água Aquaplus 100ml',
                'category': categories['peixes'],
                'brand': brands['naturallife'],
                'price': Decimal('18.90'),
                'promotional_price': None,
                'weight': Decimal('0.100'),
                'species': 'fish',
                'description': 'Condicionador de água que neutraliza cloro, cloraminas e metais pesados. Essencial para aquários.',
                'short_description': 'Condicionador de água para aquários, 100ml.',
                'is_featured': False,
            },
        ]

        created_count = 0
        updated_count = 0

        for data in products_data:
            slug = slugify(data['name'])
            # Garante slug único adicionando sufixo se necessário
            base_slug = slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(name=data['name']).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            product, created = Product.objects.update_or_create(
                name=data['name'],
                defaults={
                    'slug': slug,
                    'category': data['category'],
                    'brand': data['brand'],
                    'price': data['price'],
                    'promotional_price': data.get('promotional_price'),
                    'weight': data.get('weight'),
                    'species': data.get('species', 'all'),
                    'description': data['description'],
                    'short_description': data.get('short_description', ''),
                    'is_active': True,
                    'is_featured': data.get('is_featured', False),
                }
            )

            # Cria ou atualiza estoque
            stock_qty = random.randint(5, 50)
            Stock.objects.update_or_create(
                product=product,
                defaults={
                    'quantity': stock_qty,
                    'min_quantity': 5,
                    'reserved_quantity': 0,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f'  ✅ Criado: {product.name}')
            else:
                updated_count += 1
                self.stdout.write(f'  🔄 Atualizado: {product.name}')

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Concluído! {created_count} produtos criados, {updated_count} atualizados.'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'📦 Total de produtos no banco: {Product.objects.count()}'
        ))

    def _get_or_create_category(self, name, icon, order):
        from django.utils.text import slugify
        cat, _ = Category.objects.get_or_create(
            name=name,
            defaults={'slug': slugify(name), 'icon': icon, 'order': order, 'is_active': True}
        )
        return cat

    def _get_or_create_brand(self, name):
        from django.utils.text import slugify
        brand, _ = Brand.objects.get_or_create(
            name=name,
            defaults={'slug': slugify(name), 'is_active': True}
        )
        return brand