/* ════════════════════════════════════════════════════════
   GATEEN PETSHOP — cart.js
   Sistema global de notificações + AJAX cart
   ════════════════════════════════════════════════════════ */

/* ──────────────────────────────────────────────────────
   window.GateenNotify — sistema global de toasts
   ────────────────────────────────────────────────────── */
;(function (global) {
  'use strict';

  // Garante o container no DOM
  function getContainer() {
    var el = document.getElementById('toastTopCenter');
    if (!el) {
      el = document.createElement('div');
      el.id = 'toastTopCenter';
      document.body.appendChild(el);
    }
    return el;
  }

  var ICONS = {
    success: 'fa-check-circle',
    danger:  'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info:    'fa-info-circle',
  };

  /**
   * GateenNotify.show(message, type, duration)
   * type: 'success' | 'danger' | 'warning' | 'info'
   * duration: ms (default 3500)
   */
  function show(message, type, duration) {
    type     = type     || 'info';
    duration = duration || 3500;

    var container = getContainer();
    var icon      = ICONS[type] || 'fa-info-circle';

    var card = document.createElement('div');
    card.className = 'gateen-notification';
    card.innerHTML =
      '<span class="notif-icon ' + type + '">' +
        '<i class="fa ' + icon + '"></i>' +
      '</span>' +
      '<span class="notif-text">' + message + '</span>' +
      '<button class="notif-close" aria-label="Fechar">' +
        '<i class="fa fa-times"></i>' +
      '</button>';

    container.appendChild(card);

    // Anima entrada
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { card.classList.add('show'); });
    });

    // Fechar manualmente
    card.querySelector('.notif-close').addEventListener('click', function () {
      dismiss(card);
    });

    // Auto-dismiss
    var timer = setTimeout(function () { dismiss(card); }, duration);
    card._timer = timer;
  }

  function dismiss(card) {
    clearTimeout(card._timer);
    card.classList.remove('show');
    card.classList.add('hide');
    setTimeout(function () {
      card.parentNode && card.parentNode.removeChild(card);
    }, 350);
  }

  global.GateenNotify = { show: show };

})(window);


/* ──────────────────────────────────────────────────────
   Atualiza todos os badges de carrinho na página
   ────────────────────────────────────────────────────── */
function updateCartBadges(count) {
  document.querySelectorAll('.cart-badge-num, .cart-nav-badge').forEach(function (el) {
    if (count > 0) {
      el.textContent = count;
      el.style.display = 'flex';
    } else {
      el.style.display = 'none';
    }
  });
}


/* ──────────────────────────────────────────────────────
   AJAX Add-to-cart — delegação global
   Qualquer form com data-ajax-cart="1" ou
   botão com data-product-id funciona automaticamente.
   ────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {

  document.body.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-ajax-cart]');
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();

    var productId   = btn.dataset.productId;
    var productName = btn.dataset.productName || 'Produto';
    var quantity    = btn.dataset.quantity    || 1;

    if (!productId || !window.ADD_CART_BASE_URL) return;

    var url  = window.ADD_CART_BASE_URL + productId + '/';
    var icon = btn.querySelector('i');
    if (icon) icon.className = 'fa fa-spinner fa-spin';
    btn.disabled = true;

    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken':      window.CSRF_TOKEN || '',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type':     'application/x-www-form-urlencoded',
      },
      body: 'quantity=' + quantity,
    })
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (data) {
        if (data.success) {
          updateCartBadges(data.cart_count);
          var name = productName.length > 30
            ? productName.slice(0, 30) + '…'
            : productName;
          GateenNotify.show(name + ' adicionado ao carrinho!', 'success');
        } else {
          GateenNotify.show(data.error || 'Erro ao adicionar.', 'danger');
        }
      })
      .catch(function () {
        GateenNotify.show('Erro de conexão. Tente novamente.', 'danger');
      })
      .finally(function () {
        if (icon) icon.className = 'fa fa-cart-plus';
        btn.disabled = false;
      });
  });
});