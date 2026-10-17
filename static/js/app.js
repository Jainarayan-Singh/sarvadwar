(function () {
  'use strict';

  var root = document.documentElement;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var animated = function () { return root.getAttribute('data-motion') !== 'off' && !reduced.matches; };

  if (!animated()) document.querySelectorAll('video').forEach(function (v) { v.pause(); });

  var header = document.querySelector('[data-header]');
  var heroArt = document.querySelector('.hero-art');
  var ticking = false;
  var onScroll = function () {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () {
      ticking = false;
      if (header) header.classList.toggle('is-scrolled', window.scrollY > 8);
      if (heroArt && animated() && window.scrollY < window.innerHeight * 1.5) {
        heroArt.style.setProperty('--sy', String(Math.round(window.scrollY)));
      }
    });
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  var themeMenu = document.querySelector('[data-theme-menu]');
  if (themeMenu) {
    var button = themeMenu.querySelector('[data-theme-button]');
    var swatch = themeMenu.querySelector('[data-theme-swatch]');
    var label = themeMenu.querySelector('[data-theme-label]');
    var options = Array.prototype.slice.call(themeMenu.querySelectorAll('[data-theme-option]'));
    themeMenu.hidden = false;

    var setMenu = function (open, returnFocus) {
      themeMenu.classList.toggle('is-open', open);
      button.setAttribute('aria-expanded', String(open));
      if (open) {
        var selected = options.filter(function (o) { return o.getAttribute('aria-pressed') === 'true'; })[0];
        (selected || options[0]).focus({ preventScroll: true });
      } else if (returnFocus) {
        button.focus();
      }
    };

    var showTheme = function (id, name) {
      options.forEach(function (o) {
        o.setAttribute('aria-pressed', String(o.getAttribute('data-theme-option') === id));
      });
      swatch.className = 'swatch swatch-lg swatch-' + id;
      label.textContent = 'Theme: ' + name + '. Change theme';
    };

    var applyTheme = function (id, name) {
      var change = function () {
        root.setAttribute('data-theme', id);
        showTheme(id, name);
      };
      try { localStorage.setItem('landingTheme', id); } catch (e) {}
      if (animated() && document.startViewTransition) {
        var box = button.getBoundingClientRect();
        root.style.setProperty('--vt-x', Math.round(box.left + box.width / 2) + 'px');
        root.style.setProperty('--vt-y', Math.round(box.top + box.height / 2) + 'px');
        document.startViewTransition(change);
      } else {
        if (animated()) {
          root.classList.add('theme-transition');
          window.setTimeout(function () { root.classList.remove('theme-transition'); }, 500);
        }
        change();
      }
    };

    var current = root.getAttribute('data-theme');
    var currentOption = options.filter(function (o) { return o.getAttribute('data-theme-option') === current; })[0];
    if (currentOption) showTheme(current, currentOption.textContent.trim());

    options.forEach(function (option) {
      option.addEventListener('click', function () {
        applyTheme(option.getAttribute('data-theme-option'), option.textContent.trim());
        setMenu(false, true);
      });
    });

    button.addEventListener('click', function () { setMenu(!themeMenu.classList.contains('is-open')); });
    themeMenu.addEventListener('keydown', function (e) {
      var open = themeMenu.classList.contains('is-open');
      if (e.key === 'Escape' && open) {
        e.stopPropagation();
        setMenu(false, true);
      } else if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && open) {
        e.preventDefault();
        var i = options.indexOf(document.activeElement);
        var step = e.key === 'ArrowDown' ? 1 : -1;
        options[(i + step + options.length) % options.length].focus();
      }
    });
    document.addEventListener('click', function (e) {
      if (!themeMenu.contains(e.target)) setMenu(false);
    });
  }

  var menuButton = document.querySelector('[data-menu-toggle]');
  var nav = document.querySelector('[data-nav]');
  if (menuButton && nav) {
    menuButton.hidden = false;
    var desktop = window.matchMedia('(min-width: 48em)');
    var setNav = function (open, returnFocus) {
      menuButton.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
      if (!open && returnFocus) menuButton.focus();
    };
    menuButton.addEventListener('click', function () {
      setNav(menuButton.getAttribute('aria-expanded') !== 'true');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setNav(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') setNav(false, true);
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.site-header')) setNav(false);
    });
    desktop.addEventListener('change', function () { if (desktop.matches) setNav(false); });
  }

  document.querySelectorAll('[data-spotlight]').forEach(function (el) {
    el.addEventListener('pointermove', function (e) {
      var box = el.getBoundingClientRect();
      el.style.setProperty('--mx', Math.round(e.clientX - box.left) + 'px');
      el.style.setProperty('--my', Math.round(e.clientY - box.top) + 'px');
    });
  });

  if ('IntersectionObserver' in window && animated()) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
    document.querySelectorAll('[data-reveal]').forEach(function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight * 0.85) return;
      el.classList.add('reveal');
      observer.observe(el);
    });
  }
})();
