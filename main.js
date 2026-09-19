(() => {
  const MOBILE = window.matchMedia('(max-width: 1023px)');
  const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)');

  // ---------- Scene videos ----------
  // Each section plays its clip once when it becomes active and holds the last frame; layers crossfade via CSS.
  const layers = new Map(
    [...document.querySelectorAll('.scene-layer')].map((el) => [el.dataset.scene, el])
  );
  let activeScene = '1';

  function srcFor(scene) {
    return `media/video/scene${scene}${MOBILE.matches ? '_m' : ''}.mp4`;
  }

  function posterFor(scene) {
    if (REDUCED.matches) return `media/img/scene${scene}_last.jpg`;
    return `media/img/scene${scene}${MOBILE.matches ? '_m' : ''}_first.jpg`;
  }

  function loadSources() {
    layers.forEach((layer, scene) => {
      const video = layer.querySelector('video');
      video.poster = posterFor(scene);
      if (REDUCED.matches) {
        video.removeAttribute('src');
        video.load();
        return;
      }
      const src = srcFor(scene);
      if (!video.src.endsWith(src)) {
        video.src = src;
        video.load();
      }
    });
  }

  function playScene(scene) {
    const video = layers.get(scene)?.querySelector('video');
    if (!video || REDUCED.matches) return;
    try { video.currentTime = 0; } catch (_) { /* not loaded yet */ }
    const p = video.play();
    if (p && p.catch) p.catch(() => {});
  }

  function setScene(scene) {
    if (scene === activeScene) return;
    layers.get(activeScene)?.classList.remove('is-active');
    layers.get(scene)?.classList.add('is-active');
    activeScene = scene;
    playScene(scene);
  }

  loadSources();
  playScene('1');
  MOBILE.addEventListener('change', () => { loadSources(); playScene(activeScene); });
  REDUCED.addEventListener('change', () => { loadSources(); playScene(activeScene); });

  // ---------- Section tracking ----------
  const navLinks = [...document.querySelectorAll('.site-nav a')];
  const sections = [...document.querySelectorAll('.section[data-scene]')];

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const section = entry.target;
      setScene(section.dataset.scene);
      navLinks.forEach((a) => a.setAttribute('aria-current', String(a.hash === `#${section.id}`)));
      document.body.classList.toggle('show-cv', section.id === 'contact');
    });
  }, { rootMargin: '-45% 0px -45% 0px' });
  sections.forEach((s) => observer.observe(s));

  // ---------- Mobile menu ----------
  const toggle = document.querySelector('.menu-toggle');
  const setMenu = (open) => {
    document.body.classList.toggle('menu-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  };
  toggle.addEventListener('click', () => setMenu(!document.body.classList.contains('menu-open')));
  navLinks.forEach((a) => a.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });

  // ---------- Card stack ----------
  const stack = document.querySelector('.stack');
  if (stack) {
    let order = [...stack.children];
    const layout = () => {
      order.forEach((card, i) => {
        // Cards past the third are hidden; capping the offset keeps them from widening the page on phones.
        const d = Math.min(i, 3);
        card.style.zIndex = String(order.length - i);
        card.style.transform = `translate(${d * 7}px, ${d * 7}px) rotate(${i === 0 ? 0 : (i % 2 ? 3 : -3) * Math.min(i, 2)}deg)`;
        card.style.opacity = i > 3 ? '0' : '1';
        card.classList.toggle('is-top', i === 0);
      });
    };
    const cycle = (dx = 1, dy = 0) => {
      const top = order[0];
      top.style.transform = `translate(${dx * 420}px, ${dy * 420}px) rotate(${dx * 18}deg)`;
      top.style.opacity = '0';
      order = [...order.slice(1), top];
      setTimeout(layout, 260);
    };
    layout();
    document.querySelector('.stack-next')?.addEventListener('click', () => cycle(1, 0));

    let drag = null;
    stack.addEventListener('pointerdown', (e) => {
      const card = e.target.closest('.card');
      if (!card || card !== order[0]) return;
      drag = { card, x: e.clientX, y: e.clientY, dx: 0, dy: 0 };
      card.classList.add('is-dragging');
      card.setPointerCapture(e.pointerId);
    });
    stack.addEventListener('pointermove', (e) => {
      if (!drag) return;
      drag.dx = e.clientX - drag.x;
      drag.dy = e.clientY - drag.y;
      drag.card.style.transform = `translate(${drag.dx}px, ${drag.dy}px) rotate(${drag.dx / 18}deg)`;
    });
    const end = () => {
      if (!drag) return;
      const { card, dx, dy } = drag;
      card.classList.remove('is-dragging');
      drag = null;
      const dist = Math.hypot(dx, dy);
      if (dist > 90) cycle(dx / dist, dy / dist);
      else layout();
    };
    stack.addEventListener('pointerup', end);
    stack.addEventListener('pointercancel', end);
  }
})();
