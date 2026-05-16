/* ════════════════════════════════════════════════════════
   GATEEN — AJAX Add to Cart (Product List)
   ════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.ajax-add-cart').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation(); // não propaga para o stretched-link do card

      var productId   = this.dataset.productId;
      var productName = this.dataset.productName || 'Produto';
      var url         = ADD_CART_BASE_URL + productId + '/';

      // Feedback visual no botão
      var icon = this.querySelector('i');
      icon.className = 'fa fa-spinner fa-spin';
      this.disabled = true;

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken':     CSRF_TOKEN,
          'X-Requested-With':'XMLHttpRequest',
          'Content-Type':    'application/x-www-form-urlencoded',
        },
        body: 'quantity=1',
      })
        .then(function (res) {
          if (!res.ok) throw new Error('Erro ' + res.status);
          return res.json();
        })
        .then(function (data) {
          if (data.success) {
            // Atualiza badge do carrinho
            updateCartBadges(data.cart_count);
            // Toast de sucesso
            showToast(
              '<i class="fa fa-check-circle me-2"></i>' +
              truncate(productName, 28) + ' adicionado!',
              'success'
            );
          }
        })
        .catch(function () {
          showToast('<i class="fa fa-exclamation-circle me-2"></i>Erro ao adicionar.', 'danger');
        })
        .finally(function () {
          icon.className = 'fa fa-cart-plus';
          btn.disabled = false;
        });
    });
  });
});

/* ── Helpers ─────────────────────────────────────────────── */

function updateCartBadges(count) {
  document.querySelectorAll('.cart-badge-num').forEach(function (el) {
    if (count > 0) {
      el.textContent = count;
      el.style.display = 'inline-block';
    } else {
      el.style.display = 'none';
    }
  });
}

function truncate(str, n) {
  return str.length > n ? str.slice(0, n) + '…' : str;
}

function showToast(html, type) {
  // Remove toasts anteriores
  document.querySelectorAll('.toast-notification').forEach(function (t) {
    t.parentNode && t.parentNode.removeChild(t);
  });

  var t = document.createElement('div');
  t.className = 'toast-notification toast-' + (type || 'info');
  t.innerHTML = html;
  document.body.appendChild(t);

  requestAnimationFrame(function () {
    requestAnimationFrame(function () { t.classList.add('show'); });
  });

  setTimeout(function () {
    t.classList.remove('show');
    setTimeout(function () { t.parentNode && t.parentNode.removeChild(t); }, 300);
  }, 3200);
}