/* ════════════════════════════════════════════════════════
   GATEEN PETSHOP — JS Base
   (cart.js é carregado separadamente em base.html)
   ════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {

  // Auto-dismiss alerts após 4s
  initAlerts();

  // Scroll da navbar
  var navbar = document.querySelector('.navbar-gateen');
  if (navbar) {
    window.addEventListener('scroll', function () {
      navbar.classList.toggle('navbar-scrolled', window.scrollY > 50);
    });
  }

  // Eye icon nas senhas
  initPasswordToggles();

  // Máscaras
  initMasks();

  // CEP
  initCepLookup();

  // Smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
});

/* ── Alerts ──────────────────────────────────────────── */
function initAlerts() {
  var container = document.getElementById('messagesContainer');
  if (!container) return;
  container.querySelectorAll('.gateen-alert').forEach(function (el) {
    var timer = setTimeout(function () { dismissAlert(el, container); }, 4000);
    var btn = el.querySelector('.btn-close');
    if (btn) btn.addEventListener('click', function () {
      clearTimeout(timer); dismissAlert(el, container);
    });
  });
}

function dismissAlert(el, container) {
  el.style.transition = 'opacity .3s ease, max-height .3s ease, margin .3s ease, padding .3s ease';
  el.style.opacity = '0';
  el.style.maxHeight = el.offsetHeight + 'px';
  el.offsetHeight;
  el.style.maxHeight = '0';
  el.style.marginBottom = '0';
  el.style.paddingTop = '0';
  el.style.paddingBottom = '0';
  el.style.overflow = 'hidden';
  setTimeout(function () {
    el.parentNode && el.parentNode.removeChild(el);
    if (container && !container.querySelector('.gateen-alert')) {
      container.style.opacity = '0';
      setTimeout(function () {
        container.parentNode && container.parentNode.removeChild(container);
      }, 200);
    }
  }, 350);
}

/* ── FIX 5 — Eye icon nas senhas ─────────────────────── */
function initPasswordToggles() {
  document.querySelectorAll('.password-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var input = document.querySelector(this.dataset.target);
      if (!input) return;
      var isText = input.type === 'text';
      input.type = isText ? 'password' : 'text';
      var icon = this.querySelector('i');
      if (icon) icon.className = isText ? 'fa fa-eye' : 'fa fa-eye-slash';
    });
  });
}

/* ── Máscaras ─────────────────────────────────────────── */
function initMasks() {
  var cpf = document.querySelector('input[name="cpf"]');
  if (cpf) cpf.addEventListener('input', function () {
    var v = this.value.replace(/\D/g,'').substring(0,11);
    v = v.replace(/(\d{3})(\d)/,'$1.$2');
    v = v.replace(/(\d{3})(\d)/,'$1.$2');
    v = v.replace(/(\d{3})(\d{1,2})$/,'$1-$2');
    this.value = v;
  });

  var tel = document.querySelector('input[name="phone"]');
  if (tel) tel.addEventListener('input', function () {
    var v = this.value.replace(/\D/g,'').substring(0,11);
    if (v.length > 6) v = '('+v.substring(0,2)+') '+v.substring(2,7)+'-'+v.substring(7);
    else if (v.length > 2) v = '('+v.substring(0,2)+') '+v.substring(2);
    this.value = v;
  });
}

/* ── CEP ─────────────────────────────────────────────── */
function initCepLookup() {
  var cep = document.querySelector('input[name="cep"]');
  if (!cep) return;
  cep.addEventListener('blur', function () {
    var v = this.value.replace(/\D/g,'');
    if (v.length !== 8) return;
    fetch('https://viacep.com.br/ws/'+v+'/json/')
      .then(function(r){return r.json();})
      .then(function(d){
        if (!d.erro) {
          setField('street', d.logradouro);
          setField('neighborhood', d.bairro);
          setField('city', d.localidade);
          setField('state', d.uf);
        }
      }).catch(function(){});
  });
}

function setField(name, val) {
  var el = document.querySelector('[name="'+name+'"]');
  if (el && val) el.value = val;
}