(function () {
  var root = document.documentElement;
  root.classList.remove('no-js');
  root.classList.add('js');
  var themes = (root.getAttribute('data-themes') || '').split(',');
  var saved = null;
  try { saved = localStorage.getItem('landingTheme'); } catch (e) { saved = null; }
  if (themes.indexOf(saved) > -1) root.setAttribute('data-theme', saved);
})();
