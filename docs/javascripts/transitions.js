(() => {
  const TABS_SEL = '.md-tabs__link';
  const CONTENT_SEL = '.md-content__inner';
  const DURATION = 220; // ms — must match CSS

  // Tab order for direction detection
  const getTabLinks = () =>
    [...document.querySelectorAll(TABS_SEL)].map(a => a.getAttribute('href'));

  let currentTabIndex = -1;

  const updateCurrentTab = () => {
    const tabs = getTabLinks();
    const active = document.querySelector(`${TABS_SEL}--active`);
    currentTabIndex = active ? tabs.indexOf(active.getAttribute('href')) : -1;
  };

  // Apply an animation class, run callback, then clean up
  const animate = (el, cls, cb) => {
    el.classList.add(cls);
    const done = () => { el.classList.remove(cls); };
    // cb fires immediately (instant nav), animation plays over the new content
    if (cb) cb();
    el.addEventListener('animationend', done, { once: true });
  };

  // First load — fade in top-to-bottom
  document.addEventListener('DOMContentLoaded', () => {
    const el = document.querySelector(CONTENT_SEL);
    if (el) el.classList.add('anim-first-load');
    updateCurrentTab();
  });

  // Intercept clicks to decide animation direction
  document.addEventListener('click', e => {
    const tabLink = e.target.closest(TABS_SEL);
    const sideLink = e.target.closest('.md-nav__link:not(.md-tabs__link)');

    if (tabLink) {
      const tabs = getTabLinks();
      const nextIndex = tabs.indexOf(tabLink.getAttribute('href'));
      const dir = nextIndex > currentTabIndex ? 'anim-slide-left' : 'anim-slide-right';
      currentTabIndex = nextIndex;

      document.addEventListener('DOMContentLoaded', function handler() {
        const el = document.querySelector(CONTENT_SEL);
        if (el) animate(el, dir);
        updateCurrentTab();
        document.removeEventListener('DOMContentLoaded', handler);
      }, { once: true });
    } else if (sideLink) {
      // Sidebar: detect up/down by vertical position of the link
      const linkRect = sideLink.getBoundingClientRect();
      const mid = window.innerHeight / 2;
      const dir = linkRect.top < mid ? 'anim-slide-up' : 'anim-slide-down';

      document.addEventListener('DOMContentLoaded', function handler() {
        const el = document.querySelector(CONTENT_SEL);
        if (el) animate(el, dir);
        updateCurrentTab();
        document.removeEventListener('DOMContentLoaded', handler);
      }, { once: true });
    }
  }, true);

  // MkDocs instant nav fires a custom event after swap
  document.addEventListener('DOMContentSwitch', () => updateCurrentTab());
})();
