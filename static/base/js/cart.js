/* ═══════════════════════════════════════════════════════════
   GATEEN — cart.js
   Sistema unificado: notificações centro-topo + AJAX carrinho
   ═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* ── Configuração ────────────────────────────────────────── */
  var NOTIF_DURATION   = 4000;   // ms antes de sumir
  var CART_API_BASE    = '/pedidos/adicionar/';
  var activeTimers     = [];

  /* ─────────────────────────────────────────────────────────
     SISTEMA DE NOTIFICAÇÃO — topo centralizado
     ───────────────────────────────────────────────────────── */

  function showNotification(text, type, duration) {
    type     = type     || 'success';
    duration = duration || NOTIF_DURATION;

    var container = document.getElementById('toastTopCenter');
    if (!container) return;

    /* Remove notificações antigas se houver muitas */
    var existing = container.querySelectorAll('.gateen-notification');
    if (existing.length >= 3) {
      dismissNotification(existing[0]);
    }

    var icons = {
      success: 'fa-check',
      danger:  'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info:    'fa-info-circle',
    };

    var notif = document.createElement('div');
    notif.className = 'gateen-notification';
    notif.innerHTML =
      '<div class="notif-icon ' + type + '">' +
        '<i class="fa ' + (icons[type] || 'fa-info-circle') + '"></i>' +
      '</div>' +
      '<div class="notif-text">' + text + '</div>' +
      '<button class="notif-close" type="button" aria-label="Fechar">' +
        '<i class="fa fa-times"></i>' +
      '</button>';

    container.appendChild(notif);

    /* Anima entrada */
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        notif.classList.add('show');
      });
    });

    /* Auto-dismiss */
    var timer = setTimeout(function () {
      dismissNotification(notif);
    }, duration);
    activeTimers.push(timer);

    /* Fechar manual */
    notif.querySelector('.notif-close').addEventListener('click', function () {
      clearTimeout(timer);
      dismissNotification(notif);
    });

    return notif;
  }

  function dismissNotification(notif) {
    if (!notif || !notif.parentNode) return;
    notif.classList.remove('show');
    notif.classList.add('hide');
    setTimeout(function () {
      if (notif.parentNode) notif.parentNode.removeChild(notif);
    }, 320);
  }

  /* ── Expõe globalmente ───────────────────────────────────── */
  window.GateenNotify = { show: showNotification };

  /* Alias para compatibilidade com código antigo */
  window.GateenCart = {
    showToast: showNotification,
    updateCartBadges: updateCartBadges,
  };

  /* ─────────────────────────────────────────────────────────
     PROCESSA MENSAGENS DJANGO → centro-topo
     ───────────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    var container = document.getElementById('djangoMessages');
    if (!container) return;

    container.querySelectorAll('[data-text]').forEach(function (el, idx) {
      var tags = el.dataset.tags || '';
      var text = el.dataset.text;
      var type = 'info';
      if (tags.includes('success')) type = 'success';
      else if (tags.includes('error') || tags.includes('danger')) type = 'danger';
      else if (tags.includes('warning')) type = 'warning';

      /* Pequeno atraso entre múltiplas mensagens */
      setTimeout(function () {
        showNotification(text, type, 5000);
      }, idx * 150);
    });
  });

  /* ─────────────────────────────────────────────────────────
     BADGE DO CARRINHO
     ───────────────────────────────────────────────────────── */
  function updateCartBadges(count) {
    /* Atualiza todos os badges (suporta .cart-badge-num e .cart-nav-badge) */
    document.querySelectorAll(
      '.cart-badge-num, .cart-nav-badge'
    ).forEach(function (el) {
      el.textContent = count;
      el.style.display = count > 0 ? 'flex' : 'none';
    });
  }

  /* ─────────────────────────────────────────────────────────
     AJAX ADD TO CART — event delegation global
     ───────────────────────────────────────────────────────── */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.ajax-add-cart');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    if (btn.dataset.loading === 'true') return;

    var productId   = btn.dataset.productId;
    var productName = btn.dataset.productName || 'Produto';
    var qty         = parseInt(btn.dataset.qty || '1', 10);

    btn.dataset.loading = 'true';
    var icon = btn.querySelector('i, .fa');
    if (icon) icon.className = 'fa fa-spinner fa-spin';

    fetch(CART_API_BASE + productId + '/', {
      method:  'POST',
      headers: {
        'X-CSRFToken':      _getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type':     'application/x-www-form-urlencoded',
      },
      body: 'quantity=' + qty,
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.success) {
          updateCartBadges(data.cart_count);
          showNotification(
            '<strong>' + _trunc(data.product_name || productName, 30) +
            '</strong> adicionado ao carrinho!',
            'success'
          );
        } else {
          showNotification(
            data.error || 'Não foi possível adicionar o produto.',
            'danger'
          );
        }
      })
      .catch(function () {
        showNotification('Erro de conexão. Tente novamente.', 'danger');
      })
      .finally(function () {
        btn.dataset.loading = 'false';
        if (icon) icon.className = 'fa fa-cart-plus';
      });
  });

  /* ── Helpers ─────────────────────────────────────────────── */
  function _getCookie(name) {
    var v = '; ' + document.cookie;
    var p = v.split('; ' + name + '=');
    return p.length === 2 ? p.pop().split(';').shift() : '';
  }
  function _trunc(s, n) { return s.length > n ? s.slice(0, n) + '…' : s; }

})();