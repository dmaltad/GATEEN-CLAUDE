from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import LoyaltyAccount, LoyaltyRule, LoyaltyTransaction


LOYALTY_LEVELS = [
    ('bronze',  'Bronze',   'award',  0,    '#cd7f32'),
    ('silver',  'Prata',    'medal',  500,  '#9e9e9e'),
    ('gold',    'Ouro',     'crown',  2000, '#f39c12'),
    ('diamond', 'Diamante', 'gem',    5000, '#0288d1'),
]


@login_required
def loyalty_dashboard(request):
    account, created = LoyaltyAccount.objects.get_or_create(
        user=request.user,
        defaults={'points': 0, 'lifetime_points': 0, 'level': 'bronze'}
    )
    if created:
        account.update_level()

    transactions = LoyaltyTransaction.objects.filter(
        account=account
    ).order_by('-created_at')[:20]

    active_rules = LoyaltyRule.objects.filter(is_active=True).select_related(
        'trigger_brand', 'trigger_product', 'reward_product'
    )

    return render(request, 'loyalty/dashboard.html', {
        'account': account,
        'transactions': transactions,
        'active_rules': active_rules,
        'levels': LOYALTY_LEVELS,
    })