// Global site scripts for Ascender docs
// - Single, reliable AOS initialization
// - Re-run on Material navigation.instant page swaps

(function () {
  const initAOS = () => {
    if (!window.AOS) return;

    if (!window.__aosInitialized) {
      window.AOS.init({
        duration: 1000,
        easing: 'ease-out-cubic',
        once: false,
        offset: 100,
        delay: 0,
        disable: false,
        anchorPlacement: 'top-bottom'
      });
      window.__aosInitialized = true;
      document.documentElement.classList.add('aos-active');
    } else {
      // Already initialized: just refresh on new page content
      try {
        window.AOS.refreshHard ? window.AOS.refreshHard() : window.AOS.refresh();
      } catch (e) {
        console.warn('AOS refresh failed:', e);
      }
    }

    // Debounced resize refresh
    let resizeTimer;
    window.addEventListener('resize', () => {
      if (!window.AOS) return;
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        try {
          window.AOS.refreshHard ? window.AOS.refreshHard() : window.AOS.refresh();
        } catch {}
      }, 200);
    });
  };

  const ensureFooterLinks = () => {
    try {
      const meta = document.querySelector('.md-footer-meta__inner');
      if (!meta) return;

      // Remove any previous injected container to avoid duplicates on instant nav
      const existing = meta.querySelector('.asc-footer-links');
      if (existing) existing.remove();

      const links = window.ASC_FOOTER_LINKS || {};
      const wrap = document.createElement('div');
      wrap.className = 'asc-footer-links';

      const items = [
        { label: 'License', href: links.license },
        { label: 'Contributing', href: links.contributing },
        { label: 'Terms & Guidelines', href: links.terms },
      ];

      items.forEach((it, idx) => {
        if (!it.href) return;
        const a = document.createElement('a');
        a.href = it.href;
        a.textContent = it.label;
        wrap.appendChild(a);
        if (idx < items.length - 1) {
          const sep = document.createElement('span');
          sep.textContent = '•';
          sep.style.opacity = '0.6';
          sep.style.margin = '0 6px';
          wrap.appendChild(sep);
        }
      });

      meta.appendChild(wrap);
    } catch {}
  };

  const onEveryPageLoad = () => {
    initAOS();
    ensureFooterLinks();
  };

  if (window.document$ && typeof window.document$.subscribe === 'function') {
    // Material for MkDocs: run on every instant navigation
    window.document$.subscribe(onEveryPageLoad);
  } else {
    // Fallback: initial load
    document.addEventListener('DOMContentLoaded', onEveryPageLoad);
  }
})();
