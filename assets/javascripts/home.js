// Ascender Framework — Homepage interactions
// AOS handles scroll reveals (initialized in custom.js). This file adds the
// premium touches: particle field, cursor spotlight, magnetic buttons, copy.

(function () {
    const prefersReduced = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function initParticles() {
        if (typeof particlesJS === 'undefined') return;
        const el = document.getElementById('particles-bg');
        if (!el || el.dataset.init === '1') return;
        el.dataset.init = '1';

        particlesJS('particles-bg', {
            particles: {
                number: { value: prefersReduced ? 0 : 60, density: { enable: true, value_area: 900 } },
                color: { value: ['#DA04F6', '#7872FA', '#02FEEE', '#6413CF', '#FD8403'] },
                shape: { type: 'circle' },
                opacity: { value: 0.45, random: true, anim: { enable: true, speed: 0.6, opacity_min: 0.1 } },
                size: { value: 2.6, random: true },
                line_linked: { enable: true, distance: 150, color: '#7872FA', opacity: 0.18, width: 1 },
                move: { enable: !prefersReduced, speed: 0.9, random: true, out_mode: 'out' }
            },
            interactivity: {
                detect_on: 'window',
                events: {
                    onhover: { enable: !prefersReduced, mode: 'grab' },
                    resize: true
                },
                modes: { grab: { distance: 150, line_linked: { opacity: 0.4 } } }
            },
            retina_detect: true
        });
    }

    // Cursor-follow spotlight on glass cards (drives --mx / --my CSS vars)
    function bindSpotlight() {
        const cards = document.querySelectorAll('.feature-card, .link-card');
        cards.forEach((card) => {
            if (card.dataset.spot === '1') return;
            card.dataset.spot = '1';
            card.addEventListener('pointermove', (e) => {
                const r = card.getBoundingClientRect();
                card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
                card.style.setProperty('--my', (e.clientY - r.top) + 'px');
            });
        });
    }

    // Subtle magnetic pull on primary/secondary buttons
    function bindMagnetic() {
        if (prefersReduced) return;
        document.querySelectorAll('.ascender-home .btn').forEach((btn) => {
            if (btn.dataset.mag === '1') return;
            btn.dataset.mag = '1';
            btn.addEventListener('pointermove', (e) => {
                const r = btn.getBoundingClientRect();
                const x = e.clientX - r.left - r.width / 2;
                const y = e.clientY - r.top - r.height / 2;
                btn.style.transform = `translate(${x * 0.12}px, ${y * 0.2 - 2}px)`;
            });
            btn.addEventListener('pointerleave', () => { btn.style.transform = ''; });
        });
    }

    // Copy-to-clipboard for the install pill
    function bindCopy() {
        document.querySelectorAll('.hi-copy').forEach((btn) => {
            if (btn.dataset.copyBound === '1') return;
            btn.dataset.copyBound = '1';
            btn.addEventListener('click', async () => {
                const text = btn.getAttribute('data-copy') || '';
                try {
                    await navigator.clipboard.writeText(text);
                } catch (_) {
                    const ta = document.createElement('textarea');
                    ta.value = text; document.body.appendChild(ta);
                    ta.select(); document.execCommand('copy'); ta.remove();
                }
                const prev = btn.textContent;
                btn.textContent = '✓';
                btn.classList.add('copied');
                setTimeout(() => { btn.textContent = prev; btn.classList.remove('copied'); }, 1400);
            });
        });
    }

    function init() {
        if (!document.querySelector('.ascender-home')) return;
        initParticles();
        bindSpotlight();
        bindMagnetic();
        bindCopy();
    }

    // Run on first load and on Material instant-navigation page swaps
    if (window.document$ && typeof window.document$.subscribe === 'function') {
        window.document$.subscribe(init);
    } else {
        document.addEventListener('DOMContentLoaded', init);
    }
})();
