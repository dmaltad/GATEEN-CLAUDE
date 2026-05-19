/* ════════════════════════════════════════════════════════
   GATEEN — AJAX Add to Cart (Product List)
   ════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.ajax-add-cart').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      var productId   = this.dataset.productId;
      var productName = this.dataset.productName || 'Produto';
      var url         = ADD_CART_BASE_URL + productId + '/';
      var icon        = this.querySelector('i');

      icon.className = 'fa fa-spinner fa-spin';
      this.disabled  = true;

      fetch(url, {
        method:  'POST',
        headers: {
          'X-CSRFToken':      CSRF_TOKEN,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type':     'application/x-www-form-urlencoded',
        },
        body: 'quantity=1',
      })
        .then(function (res) {
          if (!res.ok) throw new Error('Erro ' + res.status);
          return res.json();
        })
        .then(function (data) {
          if (data.success) {
            updateCartBadges(data.cart_count);
            var name = productName.length > 30
              ? productName.slice(0, 30) + '…'
              : productName;
            GateenNotify.show(name + ' adicionado!', 'success');
          } else {
            GateenNotify.show(data.error || 'Erro ao adicionar.', 'danger');
          }
        })
        .catch(function () {
          GateenNotify.show('Erro ao adicionar.', 'danger');
        })
        .finally(function () {
          icon.className = 'fa fa-cart-plus';
          btn.disabled   = false;
        });
    });
  });
});