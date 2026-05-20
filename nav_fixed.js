// ── K8 GUIDE — Shared Navigation ─────────────────────────────────────────
// Edit this file to update the nav across ALL pages at once.

(function () {
  // Inject dropdown styles
  const style = document.createElement('style');
  style.textContent = `
    .nav-dropdown { position: relative; list-style: none; }
    .nav-dropdown > a {
      display: block; padding: .4rem 1.1rem;
      font-family: 'Share Tech Mono', monospace; font-size: .78rem; letter-spacing: 1px; text-transform: uppercase;
      color: #5a7090; text-decoration: none; border-left: 1px solid #1e2d45;
      transition: color .2s, background .2s; cursor: pointer; white-space: nowrap;
    }
    .nav-dropdown > a:hover, .nav-dropdown:hover > a { color: #00d4ff; background: rgba(0,212,255,.05); }
    .nav-dropdown > a.active { color: #00d4ff; }
    .dropdown-menu {
      display: none; position: absolute; top: 100%; left: 0;
      background: rgba(8,11,16,.97); border: 1px solid #1e2d45;
      border-top: 2px solid #e8001a; min-width: 200px; list-style: none; z-index: 999;
      backdrop-filter: blur(12px);
    }
    .nav-dropdown:hover .dropdown-menu { display: block; }
    .dropdown-menu li a {
      display: block; padding: .6rem 1.2rem;
      font-family: 'Share Tech Mono', monospace; font-size: .72rem; letter-spacing: 1px; text-transform: uppercase;
      color: #5a7090; text-decoration: none; border-bottom: 1px solid #1e2d45;
      transition: color .2s, background .2s, padding-left .2s; white-space: nowrap;
    }
    .dropdown-menu li:last-child a { border-bottom: none; }
    .dropdown-menu li a:hover { color: #00d4ff; background: rgba(0,212,255,.05); padding-left: 1.6rem; }
  `;
  document.head.appendChild(style);

  // Detect base path dynamically
  // Find the nav.js script tag to determine where the root is
  const scripts = document.querySelectorAll('script[src*="nav.js"]');
  let base = '/kn8guide/';
  if (scripts.length > 0) {
    const src = scripts[scripts.length - 1].getAttribute('src');
    // src is relative path to nav.js e.g. "nav.js", "../nav.js", "../../nav.js"
    const depth = (src.match(/\.\.\//g) || []).length;
    const parts = window.location.pathname.split('/').filter(Boolean);
    // Go up 'depth' levels from current path
    const baseParts = parts.slice(0, parts.length - depth);
    base = '/' + baseParts.join('/') + (baseParts.length ? '/' : '');
  }

  const NAV_HTML = `
<a href="${base}" class="nav-logo">K8<span>GUIDE</span></a>
<ul class="nav-links">
  <li class="nav-dropdown">
    <a href="${base}characters/">Characters ▾</a>
    <ul class="dropdown-menu">
      <li><a href="${base}characters/">Character Roster</a></li>
      <li><a href="${base}weapons/">Weapons &amp; Best Users</a></li>
      <li><a href="${base}tracker/">Character Tracker</a></li>
    </ul>
  </li>
  <a href="${base}beginner/">Beginner</a>
  <li class="nav-dropdown">
    <a href="${base}gameguide/">Game Guide ▾</a>
    <ul class="dropdown-menu">
      <li><a href="${base}gameguide/">Game Guide</a></li>
      <li><a href="${base}limited/">Limited Characters</a></li>
    </ul>
  </li>
  <a href="${base}combat/">Combat</a>
  <a href="${base}socials/">Socials</a>
</ul>`;

  // Inject nav
  const nav = document.getElementById('main-nav');
  if (nav) nav.innerHTML = NAV_HTML;

  // Highlight active page
  const currentPath = window.location.pathname;
  document.querySelectorAll('#main-nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    if (currentPath === href || currentPath === href.replace(/\/$/, '')) {
      link.classList.add('active');
      const dropdown = link.closest('.nav-dropdown');
      if (dropdown) dropdown.querySelector(':scope > a').classList.add('active');
    }
  });
})();
