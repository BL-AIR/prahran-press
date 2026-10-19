/* Prahran Publishing — light / dark toggle.
   Follows the visitor's system setting until they choose; the choice is remembered on this device.
   (The saved choice is applied before first paint by a one-line script in each page's <head>.) */
(function () {
  'use strict';
  var toggle = document.querySelector('.theme-toggle');
  if (!toggle) return;
  var root = document.documentElement;
  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  var isDark = function () {
    var t = root.getAttribute('data-theme');
    return t ? t === 'dark' : !!(mq && mq.matches);
  };
  var label = function () {
    toggle.setAttribute('aria-label', isDark() ? 'Switch to light mode' : 'Switch to dark mode');
  };
  label();
  if (mq && mq.addEventListener) mq.addEventListener('change', label);
  toggle.addEventListener('click', function () {
    var next = isDark() ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('prahran-theme', next); } catch (e) {}
    label();
  });
})();
