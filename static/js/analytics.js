(function () {
  var me = document.currentScript;
  if (!me) return;
  var provider = me.getAttribute('data-provider');
  var id = me.getAttribute('data-id');
  var src = me.getAttribute('data-src');
  if (!provider || !id || !src) return;
  var s = document.createElement('script');
  s.async = true;
  if (provider === 'plausible') {
    s.defer = true;
    s.setAttribute('data-domain', id);
    s.src = src;
  } else if (provider === 'ga4') {
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', id);
    s.src = src + '?id=' + encodeURIComponent(id);
  } else {
    return;
  }
  document.head.appendChild(s);
})();
