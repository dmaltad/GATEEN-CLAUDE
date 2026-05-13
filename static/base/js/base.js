// ==============================
// GATEEN PETSHOP — JS BASE
// ==============================

document.addEventListener('DOMContentLoaded', function () {

  // Auto-dismiss alerts after 4s
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 4000);
  });

  // Add to cart — AJAX
  document.querySelectorAll('.add-cart-btn[data-product-id]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var productId = this.dataset.productId;
      var csrfToken = getCookie('csrftoken');

      fetch('/pedidos/adicionar/' + productId + '/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'quantity=1',
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.success) {
            updateCartBadge(data.cart_count);
            showToast('Produto adicionado ao carrinho!', 'success');
          }
        })
        .catch(function () {
          showToast('Erro ao adicionar. Tente novamente.', 'danger');
        });
    });
  });

  // Quantity input — prevent negatives
  document.querySelectorAll('input[type="number"]').forEach(function (input) {
    input.addEventListener('change', function () {
      if (parseInt(this.value) < 1) this.value = 1;
    });
  });

  // Smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Navbar scroll effect
  var navbar = document.querySelector('.navbar-gateen');
  if (navbar) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 50) {
        navbar.classList.add('navbar-scrolled');
      } else {
        navbar.classList.remove('navbar-scrolled');
      }
    });
  }

  // CEP auto-fill
  var cepInput = document.querySelector('input[name="cep"]');
  if (cepInput) {
    cepInput.addEventListener('blur', function () {
      var cep = this.value.replace(/\D/g, '');
      if (cep.length === 8) {
        fetch('https://viacep.com.br/ws/' + cep + '/json/')
          .then(function (r) { return r.json(); })
          .then(function (data) {
            if (!data.erro) {
              setFieldValue('street', data.logradouro);
              setFieldValue('neighborhood', data.bairro);
              setFieldValue('city', data.localidade);
              setFieldValue('state', data.uf);
            }
          });
      }
    });
  }

  // CPF mask
  var cpfInput = document.querySelector('input[name="cpf"]');
  if (cpfInput) {
    cpfInput.addEventListener('input', function () {
      var v = this.value.replace(/\D/g, '').substring(0, 11);
      v = v.replace(/(\d{3})(\d)/, '$1.$2');
      v = v.replace(/(\d{3})(\d)/, '$1.$2');
      v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
      this.value = v;
    });
  }

  // Phone mask
  var phoneInput = document.querySelector('input[name="phone"]');
  if (phoneInput) {
    phoneInput.addEventListener('input', function () {
      var v = this.value.replace(/\D/g, '').substring(0, 11);
      if (v.length > 6) {
        v = '(' + v.substring(0, 2) + ') ' + v.substring(2, 7) + '-' + v.substring(7);
      } else if (v.length > 2) {
        v = '(' + v.substring(0, 2) + ') ' + v.substring(2);
      }
      this.value = v;
    });
  }

});

// ==============================
// HELPERS
// ==============================

function getCookie(name) {
  var value = '; ' + document.cookie;
  var parts = value.split('; ' + name + '=');
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

function updateCartBadge(count) {
  var badges = document.querySelectorAll('.cart-badge, [data-cart-badge]');
  badges.forEach(function (badge) {
    badge.textContent = count;
    badge.style.display = count > 0 ? 'inline' : 'none';
  });
}

function showToast(message, type) {
  type = type || 'success';
  var toast = document.createElement('div');
  toast.className = 'toast-notification toast-' + type;
  toast.innerHTML =
    '<i class="fa fa-' + (type === 'success' ? 'check-circle' : 'exclamation-circle') + ' me-2"></i>' +
    message;
  document.body.appendChild(toast);
  setTimeout(function () { toast.classList.add('show'); }, 10);
  setTimeout(function () {
    toast.classList.remove('show');
    setTimeout(function () { toast.remove(); }, 300);
  }, 3000);
}

function setFieldValue(name, value) {
  var field = document.querySelector('[name="' + name + '"]');
  if (field && value) field.value = value;
}