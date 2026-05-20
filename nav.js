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
  const NAV_HTML = `
<a href="/" class="nav-logo">K8<span>GUIDE</span></a>
<ul class="nav-links">
  <li class="nav-dropdown">
    <a href="/characters/">Characters ▾</a>
    <ul class="dropdown-menu">
      <li><a href="/characters/">Character Roster</a></li>
      <li><a href="/weapons/">Weapons &amp; Best Users</a></li>
      <li><a href="/tracker/">Character Tracker</a></li>
    </ul>
  </li>
  <a href="/beginner/">Beginner</a>
  <li class="nav-dropdown">
    <a href="/gameguide/">Game Guide ▾</a>
    <ul class="dropdown-menu">
      <li><a href="/gameguide/">Game Guide</a></li>
      <li><a href="/limited/">Limited Characters</a></li>
    </ul>
  </li>
  <a href="/combat/">Combat</a>
  <a href="/socials/">Socials</a>
</ul>`;

  // Inject nav
  const nav = document.getElementById('main-nav');
  if (nav) nav.innerHTML = NAV_HTML;

  // Highlight active page
  const current = window.location.pathname.replace(/\/$/, '').split('/').pop() || '';
  document.querySelectorAll('#main-nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    const hrefClean = href.replace(/\/$/, '').split('/').pop() || '';
    if (hrefClean === current) {
      link.classList.add('active');
      // If inside a dropdown, also highlight the parent
      const dropdown = link.closest('.nav-dropdown');
      if (dropdown) dropdown.querySelector(':scope > a').classList.add('active');
    }
  });
})();
