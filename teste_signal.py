# python manage.py shell
from apps.orders.models import Order
from apps.loyalty.models import LoyaltyAccount, LoyaltyTransaction

# Verifica se o signal está sendo chamado
order = Order.objects.last()
print(f'Pedido: {order.order_number} | Total: {order.total}')

account = LoyaltyAccount.objects.filter(user=order.user).first()
print(f'Pontos: {account.points if account else "conta não criada"}')

txs = LoyaltyTransaction.objects.filter(order=order)
print(f'Transações: {txs.count()}')
for tx in txs:
    print(f'  → {tx.transaction_type} | {tx.points} pts | {tx.description}')