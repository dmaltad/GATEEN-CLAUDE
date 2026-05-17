/* ════════════════════════════════════════════════════════
   GATEEN — cart.js  (global cart AJAX + toast system)
   ════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  // ── Toast container ─────────────────────────────────────
  var _toastQueue = [];
  var _toastShowing = false;

  function showToast(html, type, duration) {
    _toastQueue.push({ html: html, type: type || 'info', duration: duration || 3500 });
    if (!_toastShowing) _nextToast();
  }

  function _nextToast() {
    if (!_toastQueue.length) { _toastShowing = false; return; }
    _toastShowing = true;
    var item = _toastQueue.shift();

    // Remove toasts existentes
    document.querySelectorAll('.gateen-toast').forEach(function (t) {
      t.parentNode && t.parentNode.removeChild(t);
    });

    var el = document.createElement('div');
    el.className = 'toast-notification gateen-toast toast-' + item.type;
    el.innerHTML = item.html;
    document.body.appendChild(el);

    requestAnimationFrame(function () {
      requestAnimationFrame(function () { el.classList.add('show'); });
    });

    setTimeout(function () {
      el.classList.remove('show');
      setTimeout(function () {
        el.parentNode && el.parentNode.removeChild(el);
        setTimeout(_nextToast, 200);
      }, 300);
    }, item.duration);
  }

  // ── Atualiza badge do carrinho ───────────────────────────
  function updateCartBadges(count) {
    document.querySelectorAll('.cart-badge-num').forEach(function (el) {
      el.textContent = count;
      el.style.display = count > 0 ? 'flex' : 'none';
    });
  }

  // ── AJAX Add to Cart ─────────────────────────────────────
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.ajax-add-cart');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    if (btn.dataset.loading === 'true') return;

    var productId   = btn.dataset.productId;
    var productName = btn.dataset.productName || 'Produto';
    var qty         = parseInt(btn.dataset.qty || '1', 10);
    var url         = '/pedidos/adicionar/' + productId + '/';

    btn.dataset.loading = 'true';
    var icon = btn.querySelector('i, .fa');
    if (icon) icon.className = 'fa fa-spinner fa-spin';

    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'quantity=' + qty,
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.success) {
          updateCartBadges(data.cart_count);
          showToast(
            '<i class="fa fa-check-circle me-2" style="color:var(--success);"></i>' +
            _trunc(data.product_name || productName, 30) + ' adicionado!',
            'success'
          );
        }
      })
      .catch(function () {
        showToast('<i class="fa fa-exclamation-circle me-2"></i>Erro ao adicionar.', 'danger');
      })
      .finally(function () {
        btn.dataset.loading = 'false';
        if (icon) icon.className = 'fa fa-cart-plus';
      });
  });

  // ── Processa mensagens Django como toasts ────────────────
  document.addEventListener('DOMContentLoaded', function () {
    var container = document.getElementById('djangoMessages');
    if (!container) return;

    container.querySelectorAll('[data-text]').forEach(function (el) {
      var tags = el.dataset.tags || '';
      var text = el.dataset.text;
      var type = 'info';
      if (tags.includes('success')) type = 'success';
      else if (tags.includes('error') || tags.includes('danger')) type = 'danger';
      else if (tags.includes('warning')) type = 'warning';

      var icons = {
        success: 'check-circle',
        danger:  'exclamation-circle',
        warning: 'exclamation-triangle',
        info:    'info-circle',
      };

      showToast(
        '<i class="fa fa-' + (icons[type] || 'info-circle') + ' me-2"></i>' + text,
        type,
        4500
      );
    });
  });

  // ── Helpers ─────────────────────────────────────────────
  function getCookie(name) {
    var v = '; ' + document.cookie;
    var p = v.split('; ' + name + '=');
    return p.length === 2 ? p.pop().split(';').shift() : '';
  }

  function _trunc(s, n) { return s.length > n ? s.slice(0, n) + '…' : s; }

  // API pública
  window.GateenCart = { showToast: showToast, updateCartBadges: updateCartBadges };
})();