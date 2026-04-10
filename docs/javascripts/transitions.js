(() => {
  const CLASSES = ['anim-left','anim-right','anim-up','anim-down','anim-fadein'];

  const play = (cls) => {
    const el = document.querySelector('.md-content__inner');
    if (!el) return;
    el.classList.remove(...CLASSES);
    void el.offsetWidth;
    el.classList.add(cls);
  };

  const tabHrefs = () =>
    [...document.querySelectorAll('.md-tabs__link')].map(a => a.href);

  let prevHref = location.href;
  let pendingClass = null;

  document.addEventListener('click', e => {
    const tab  = e.target.closest('.md-tabs__link');
    const side = e.target.closest('.md-nav__link:not(.md-tabs__link)');
    if (tab) {
      const tabs = tabHrefs();
      const pi = tabs.findIndex(h => prevHref.startsWith(h));
      const ni = tabs.indexOf(tab.href);
      pendingClass = ni >= pi ? 'anim-left' : 'anim-right';
    } else if (side) {
      const rect = side.getBoundingClientRect();
      pendingClass = rect.top < window.innerHeight / 2 ? 'anim-up' : 'anim-down';
    }
  }, true);

  const init = () => {
    // First load
    play('anim-fadein');
    prevHref = location.href;

    // Every instant-nav swap
    window.document$.subscribe(() => {
      play(pendingClass || 'anim-fadein');
      pendingClass = null;
      prevHref = location.href;
    });
  };

  // Wait for Material to expose window.document$
  if (window.document$) {
    init();
  } else {
    const iv = setInterval(() => {
      if (window.document$) { clearInterval(iv); init(); }
    }, 10);
  }
})();
