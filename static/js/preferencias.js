/*
 * Preferencias visuales del usuario: modo día/noche y tamaño de texto.
 * Se guardan en localStorage (solo en este navegador). Si el navegador no
 * permite localStorage (modo privado, etc.) la página sigue funcionando.
 * La aplicación inicial se hace en un <script> en el <head> de base.html
 * para evitar el "parpadeo" de colores al cargar.
 */
(function () {
  'use strict';

  var CLAVE_TEMA = 'rodamar-tema';
  var CLAVE_FUENTE = 'rodamar-fuente';
  var NIVELES = [87.5, 100, 112.5, 125, 137.5, 150]; // % del tamaño base
  var raiz = document.documentElement;

  function leer(clave) {
    try { return localStorage.getItem(clave); } catch (e) { return null; }
  }
  function guardar(clave, valor) {
    try { localStorage.setItem(clave, valor); } catch (e) { /* sin almacenamiento */ }
  }

  /* ---------------- Modo día / noche ---------------- */
  function temaActual() {
    return raiz.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
  }

  function aplicarTema(tema) {
    raiz.setAttribute('data-bs-theme', tema);
    var boton = document.getElementById('btn-tema');
    if (boton) {
      var oscuro = tema === 'dark';
      boton.querySelector('.icono-tema').textContent = oscuro ? '☀️' : '🌙';
      boton.querySelector('.texto-tema').textContent = oscuro ? 'Modo día' : 'Modo noche';
      boton.setAttribute('aria-pressed', oscuro ? 'true' : 'false');
      boton.setAttribute('title', oscuro ? 'Cambiar a modo día' : 'Cambiar a modo noche');
    }
  }

  /* ---------------- Tamaño de texto ---------------- */
  function nivelActual() {
    var guardado = parseFloat(leer(CLAVE_FUENTE));
    return NIVELES.indexOf(guardado) >= 0 ? guardado : 100;
  }

  function aplicarFuente(porcentaje) {
    raiz.style.fontSize = porcentaje + '%';
    var etiqueta = document.getElementById('acc-fuente-valor');
    if (etiqueta) { etiqueta.textContent = Math.round(porcentaje) + '%'; }
    var menos = document.getElementById('acc-fuente-menos');
    var mas = document.getElementById('acc-fuente-mas');
    if (menos) { menos.disabled = porcentaje <= NIVELES[0]; }
    if (mas) { mas.disabled = porcentaje >= NIVELES[NIVELES.length - 1]; }
  }

  function cambiarFuente(paso) {
    var i = NIVELES.indexOf(nivelActual());
    var nuevo = NIVELES[Math.min(NIVELES.length - 1, Math.max(0, i + paso))];
    guardar(CLAVE_FUENTE, String(nuevo));
    aplicarFuente(nuevo);
  }

  document.addEventListener('DOMContentLoaded', function () {
    aplicarTema(temaActual());
    aplicarFuente(nivelActual());

    var botonTema = document.getElementById('btn-tema');
    if (botonTema) {
      botonTema.addEventListener('click', function () {
        var nuevo = temaActual() === 'dark' ? 'light' : 'dark';
        guardar(CLAVE_TEMA, nuevo);
        aplicarTema(nuevo);
      });
    }

    var menos = document.getElementById('acc-fuente-menos');
    var mas = document.getElementById('acc-fuente-mas');
    var reset = document.getElementById('acc-fuente-reset');
    if (menos) { menos.addEventListener('click', function (e) { e.stopPropagation(); cambiarFuente(-1); }); }
    if (mas) { mas.addEventListener('click', function (e) { e.stopPropagation(); cambiarFuente(1); }); }
    if (reset) {
      reset.addEventListener('click', function (e) {
        e.stopPropagation();
        guardar(CLAVE_FUENTE, '100');
        aplicarFuente(100);
      });
    }

    // Atajos de teclado: Alt + "+" / Alt + "-" / Alt + 0
    document.addEventListener('keydown', function (e) {
      if (!e.altKey) { return; }
      if (e.key === '+' || e.key === '=') { e.preventDefault(); cambiarFuente(1); }
      else if (e.key === '-') { e.preventDefault(); cambiarFuente(-1); }
      else if (e.key === '0') { e.preventDefault(); guardar(CLAVE_FUENTE, '100'); aplicarFuente(100); }
    });
  });
})();
