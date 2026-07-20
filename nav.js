// ── K8 GUIDE — Shared Navigation ─────────────────────────────────────────
// Edit this file to update the nav across ALL pages at once.

(function () {
  // Inject dropdown + mobile nav styles
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

    /* ── MOBILE NAV ─────────────────────────────────────────── */
    .nav-burger {
      display: none; flex-direction: column; justify-content: center; gap: 5px;
      width: 32px; height: 32px; background: none; border: none; cursor: pointer; padding: 0;
      z-index: 1001;
    }
    .nav-burger span {
      display: block; width: 100%; height: 2px; background: #c8d8ea; transition: transform .25s, opacity .25s;
    }
    .nav-burger.open span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
    .nav-burger.open span:nth-child(2) { opacity: 0; }
    .nav-burger.open span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

    .nav-mobile-overlay {
      display: none; position: fixed; inset: 0; top: 56px; background: rgba(5,7,11,.98);
      backdrop-filter: blur(8px); z-index: 998; overflow-y: auto;
      -webkit-overflow-scrolling: touch;
    }
    .nav-mobile-overlay.open { display: block; }

    @media (max-width: 880px) {
      .nav-links { display: none; }
      .nav-burger { display: flex; }

      .nav-mobile-overlay .nav-links {
        display: flex; flex-direction: column; width: 100%; padding: 1rem 0 3rem;
      }
      .nav-mobile-overlay .nav-links > a,
      .nav-mobile-overlay .nav-dropdown > a {
        padding: 1rem 1.5rem; font-size: .85rem; border-left: none;
        border-bottom: 1px solid #1e2d45; width: 100%;
      }
      .nav-mobile-overlay .nav-links a:last-child { border-right: none; }

      .nav-mobile-overlay .nav-dropdown > a {
        display: flex; align-items: center; justify-content: space-between;
      }
      .nav-mobile-overlay .nav-dropdown > a::after {
        content: '+'; font-size: 1.1rem; color: #5a7090; transition: transform .2s;
      }
      .nav-mobile-overlay .nav-dropdown.open > a::after { content: '−'; }

      .nav-mobile-overlay .dropdown-menu {
        display: none; position: static; border: none; border-top: none;
        background: rgba(0,0,0,.25); backdrop-filter: none; min-width: 0;
      }
      .nav-mobile-overlay .nav-dropdown.open .dropdown-menu { display: block; }
      .nav-mobile-overlay .dropdown-menu li a {
        padding: .9rem 2.2rem; font-size: .78rem; border-bottom: 1px solid rgba(30,45,69,.5);
      }
      .nav-mobile-overlay .dropdown-menu li a:hover { padding-left: 2.2rem; }
    }
  `;
  document.head.appendChild(style);

  // Base path - dynamically detected so this works on any repo/clone
  // (e.g. the live site at /kn8guide/, a staging copy at /kn8-test-/, etc.)
  // GitHub Pages project sites always serve from /<repo-name>/, so we grab
  // the first path segment from the current URL instead of hardcoding it.
  // On a custom domain (e.g. kn8guide.xyz), there is no repo-name segment,
  // so we only treat the first segment as a base path if it's not already
  // one of our known top-level site folders (meaning: if it looks like a
  // page path, not a repo name, base should just be '/').
  const KNOWN_TOP_LEVEL = ['characters','weapons','tracker','squadmaker','tierlist','beginner','banners','limited','gameguide','combat','announcements','socials','feedback','data','kn8 characters','vote','fan-zone'];
  const pathParts = window.location.pathname.split('/').filter(Boolean);
  let base = '/';
  if (pathParts.length > 0 && !KNOWN_TOP_LEVEL.includes(pathParts[0].toLowerCase())) {
    base = '/' + pathParts[0] + '/';
  }

  const NAV_HTML = `
<a href="${base}" class="nav-logo">K8<span>GUIDE</span></a>
<button class="nav-burger" id="navBurger" aria-label="Open menu">
  <span></span><span></span><span></span>
</button>
<ul class="nav-links">
  <li class="nav-dropdown">
    <a href="${base}characters/">Characters ▾</a>
    <ul class="dropdown-menu">
      <li><a href="${base}characters/">Character Roster</a></li>
      <li><a href="${base}weapons/">Weapons &amp; Best Users</a></li>
      <li><a href="${base}tracker/">Character Tracker</a></li>
      <li><a href="${base}squadmaker/">Squad Maker</a></li>
      <li><a href="${base}tierlist/">Tier List Maker</a></li>
    </ul>
  </li>
  <a href="${base}beginner/">Beginner</a>
  <li class="nav-dropdown">
    <a href="${base}banners/">Banners ▾</a>
    <ul class="dropdown-menu">
      <li><a href="${base}banners/">Current &amp; Upcoming</a></li>
      <li><a href="${base}limited/">Limited Characters</a></li>
    </ul>
  </li>
  <li class="nav-dropdown">
    <a href="${base}gameguide/">Game Guide ▾</a>
    <ul class="dropdown-menu">
      <li><a href="${base}gameguide/">Game Guide</a></li>
      <li><a href="${base}gameguide/gacha/">Gacha &amp; Pulling</a></li>
      <li><a href="${base}gameguide/story/">Story Modes</a></li>
      <li><a href="${base}gameguide/events/">Events</a></li>
      <li><a href="${base}gameguide/exploit-medals/">Exploit Medals</a></li>
      <li><a href="${base}gameguide/currencies/">Currencies</a></li>
      <li><a href="${base}gameguide/synthesis/">Material Synthesis</a></li>
      <li><a href="${base}gameguide/spec-ops/">Spec-Ops Rank</a></li>
      <li><a href="${base}gameguide/progression/">Character Progression</a></li>
      <li><a href="${base}gameguide/unlocked-potential/">Unlocked Potential</a></li>
      <li><a href="${base}gameguide/achievements/">Unknown Achievements</a></li>
    </ul>
  </li>
  <li class="nav-dropdown">
    <a href="${base}combat/">Combat ▾</a>
    <ul class="dropdown-menu">
      <li><a href="${base}combat/">Combat Overview</a></li>
      <li><a href="${base}combat/mechanics/">Core Mechanics</a></li>
      <li><a href="${base}combat/status-effects/">Status Effects</a></li>
      <li><a href="${base}combat/elements/">Elements &amp; Damage Types</a></li>
      <li><a href="${base}combat/uniparts/">Uniparts &amp; Set Effects</a></li>
    </ul>
  </li>
  <a href="${base}announcements/">Announcements</a>
  <li class="nav-dropdown">
    <a href="${base}fan-zone/">Fan Zone ▾</a>
    <ul class="dropdown-menu">
      <li><a href="${base}fan-zone/">Fan Zone Home</a></li>
      <li><a href="${base}vote/">Character Poll</a></li>
    </ul>
  </li>
  <a href="${base}socials/">Socials</a>
  <a href="${base}feedback/">Feedback</a>
</ul>`;

  // Inject nav into the main bar
  const nav = document.getElementById('main-nav');
  if (nav) nav.innerHTML = NAV_HTML;

  // Build the mobile overlay panel as a clone of the same nav links,
  // so updating the link list above updates both desktop and mobile.
  const overlay = document.createElement('div');
  overlay.className = 'nav-mobile-overlay';
  overlay.id = 'navMobileOverlay';
  const linksClone = nav ? nav.querySelector('.nav-links').cloneNode(true) : null;
  if (linksClone) overlay.appendChild(linksClone);
  if (nav) nav.insertAdjacentElement('afterend', overlay);

  // Burger toggle
  const burger = document.getElementById('navBurger');
  if (burger) {
    burger.addEventListener('click', () => {
      const isOpen = overlay.classList.toggle('open');
      burger.classList.toggle('open', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });
  }

  // Tap-to-expand accordion behavior inside the mobile overlay only.
  // Desktop hover dropdowns are untouched (handled by CSS :hover).
  if (linksClone) {
    linksClone.querySelectorAll(':scope > .nav-dropdown > a').forEach(link => {
      link.addEventListener('click', e => {
        e.preventDefault();
        const dropdown = link.closest('.nav-dropdown');
        const wasOpen = dropdown.classList.contains('open');
        linksClone.querySelectorAll('.nav-dropdown').forEach(d => d.classList.remove('open'));
        if (!wasOpen) dropdown.classList.add('open');
      });
    });
    // Close the mobile menu after tapping an actual destination link
    // (i.e. any link inside a dropdown submenu, or a top-level link
    // that isn't itself a dropdown toggle).
    linksClone.querySelectorAll('.dropdown-menu a').forEach(link => {
      link.addEventListener('click', () => {
        overlay.classList.remove('open');
        burger.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
    linksClone.querySelectorAll(':scope > a').forEach(link => {
      link.addEventListener('click', () => {
        overlay.classList.remove('open');
        burger.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  // Highlight active page (applies to both desktop nav and mobile overlay clone)
  const currentPath = window.location.pathname;
  document.querySelectorAll('#main-nav a, #navMobileOverlay a').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    if (currentPath === href || currentPath === href.replace(/\/$/, '')) {
      link.classList.add('active');
      const dropdown = link.closest('.nav-dropdown');
      if (dropdown) {
        const toggle = dropdown.querySelector(':scope > a');
        if (toggle) toggle.classList.add('active');
      }
    }
  });
})();
